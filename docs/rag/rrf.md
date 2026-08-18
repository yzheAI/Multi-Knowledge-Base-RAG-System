# RRF

## 1. RRF概述

RRF是一种用于融合多个检索结果的排序方法。在本项目中，分别使用FAISS和BM25进行检索：
- FAISS：基于向量相似度进行语义检索
- BM25：基于关键词匹配进行检索
- RRF：融合FAISS和BM25的检索排名
- CrossEncoder：对融合后的候选Chunk进行最终重排序

整体流程：
```text
User Query
    |
    +------------------+
    |                  |
    v                  v
FAISS Search       BM25 Search
Top 20              Top 20
    |                  |
    +--------+---------+
             |
             v
        RRF Fusion
             |
          Top 10
             |
             v
      CrossEncoder
             |
          Top 5
```

## 2. 为什么需要RRF

FAISS和BM25检索方式不同，各自具有不同的优势。
FAISS负责语义相似度检索，BM25负责关键词匹配度检索，
二者在Retrieval中实现了优势互补，在检索增强生成中拥有良好的效果。
但是FAISS的score和BM25的score不能直接相加，例如：
```text
FAISS：
A = 0.82
B = 0.79
C = 0.76

BM25：
C = 13.2
A = 11.5
B = 8.7
```
两个模型的分数不是同一个尺度，也没有直接可比性。
RRF的核心思想是：不关注不同检索方式的具体分数，将不同Chunk在不同检索方式中的排名作为判断标准。
这种方式在检索结果融合时不需要进行归一化等操作，充分利用FAISS和BM25的互补性。

## 3. RRF原理
RRF不需要直接比较不同检索器的原始分数，而是根据文档在各个检索结果中的排名进行融合。
RRF基本公式:
```
RRF(d) = Σ (1/(k+r))，其中 r ∈ R(d)
```
- d：文档块chunk
- R(d)：文档d在各个检索器返回结果中的排名集合
- k：RRF超参，代码设置k=40

例如一个Chunk：
```text
FAISS rank = 2
BM25 rank = 5
```
那么：
```text
RRF score =
1 / (k + 2)
+
1 / (k + 5)
```
如果一个Chunk同时出现在FAISS和BM25的结果中，它会获得两路排名贡献，因此通常可以获得较高的融合排名。

## 4. RRF的作用

RRF不会重新计算Query和Chunk的语义相似度，也不会进行关键词匹配度检索，
而是将多个检索器产生的排序结果统一融合成一个新的排序结果。
例如：
```text
FAISS: A B C D
BM25: C E A F
```
经过RRF融合排序后：
```text
RRF: A C B E F D
```
其中A和C同时被两个检索器召回，因此能够获得两路排名贡献。

## 5. 项目中的实现

### 5.1 scores

```text
scores = {}
```
用于保存每个Chunk的RRF分数：chunk_id → RRF score
例如：
```text
{
    101: 0.04,
    205: 0.03,
    306: 0.02
}
```

### 5.2 docs_map

```text
docs_map = {}
```
用于保存：chunk_id → doc
因为RRF计算过程中主要使用chunk_id和排名，因此最终排序完成后需要根据chunk_id找回完整的Chunk信息。

### 5.3 处理FAISS结果
```text
for rank, doc in enumerate(
        faiss_docs,
        start=1
):
```
使用enumerate获取FAISS检索结果的排名，并且使用start=1规定排名从1开始：
```text
第一个 Chunk → rank = 1
第二个 Chunk → rank = 2
第三个 Chunk → rank = 3
```
然后计算 1/ (k + rank)
得到该Chunk在FAISS检索结果中的RRF贡献。

### 5.4 处理BM25结果
BM25使用相同的方法计算排名贡献：
```text
scores[chunk_id] = (
    scores.get(chunk_id, 0)
    +
    1 / (k + rank)
)
```
如果Chunk已经被FAISS召回，则scores[chunk_id]中已经存在FAISS的贡献，
则此时BM25再次召回该Chunk，就会继续累加BM25的贡献。因此：
```text
FAISS + BM25
     ↓
同一个 Chunk
     ↓
两个排名贡献相加
```

## 6. RRF排序
得到所有Chunk的RRF分数后：
```text
ranked = sorted(
    scores.items(),
    key=lambda x: x[1],
    reverse=True
)
```
按照RRF score从高到低进行排序。
```text
return [
    docs_map[chunk_id]
    for chunk_id, score in ranked
]
```
最终根据排序后的chunk_id召回完整的Chunk。

## 7. k参数

RRF中的k用于控制各路检索的排名贡献随排名下降的速度。
因此使用 1/(k+r)
当k较小时，高排名和低排名之间的差异会非常明显，
当k较大时，高排名和低排名之间的差距会得到缩小。
本项目当前使用 k=40，并对k=20, 40, 60进行了测试，
在当前的测试集下不同的k对检索结果没有明显影响，因此暂时使用k=40。

## 8. RRF在项目中的位置
RRF位于FAISS和BM25之后，CrossEncoder之前：
```text
Query
  |
  +-------------------+
  |                   |
  v                   v
Embedding          Jieba Tokenizer
  |                   |
  v                   v
FAISS              BM25
Top 20             Top 20
  |                   |
  +---------+---------+
            |
            v
       RRF Fusion
            |
          Top 10
            |
            v
      CrossEncoder
            |
          Top 5
```
RRF的作用是将两路检索结果进行融合，为CrossEncoder提供更加合理的候选集合。

## 9. 实验验证

为了验证 RRF 在 Hybrid Retrieval 中的实际作用，对比了以下方案：

- Merge
- RRF Fusion
- Merge + Reranker
- RRF Fusion + Reranker

实验结果表明，RRF Fusion + Reranker 的整体表现最好，其中：

- Recall@1：63.79%
- Recall@3：86.21%
- Recall@5：87.93%
- MRR：74.28%

完整的实验结果和不同方案的详细对比见 `retrieval_evaluation.md`。

## 10. 当前优点

- 兼顾语义检索与关键词检索
- 不依赖不同检索器的原始分数
- 计算成本较低
- 对多路检索器具有较好的扩展性

## 11. 未来优化方向

### 11.1 动态调整RRF参数

当前项目使用固定的k=40，
后续可根据不同的Query类型、知识库规模或检索结果特征动态调整k。
进一步可以研究加权RRF，通过不同权重控制FAISS和BM25对最终排名的影响。

### 11.2 分析不同检索器的互补性

当前 Hybrid Retrieval 已经证明相比单独使用 FAISS 或 BM25 能够取得更好的效果。

未来可以进一步统计：

- FAISS 和 BM25 Top-K 的重合率
- 仅被 FAISS 召回的正确 Chunk 数量
- 仅被 BM25 召回的正确 Chunk 数量
- 两者共同召回的正确 Chunk 数量
从而更加准确地判断两种检索方式的互补程度。







