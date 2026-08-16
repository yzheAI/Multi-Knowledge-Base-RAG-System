# FAISS

## 1. 模块概述

FAISS (Facebook AI Similarity Search) 是一个用于高效相似度搜索和向量聚类的开源库。

在项目中，FAISS主要负责：
- 保存Chunk所对应的Embedding向量
- 根据Query Embedding进行向量相似度检索
- 返回Top-K个最相似的Chunk ID
- 将向量索引持久化到本地磁盘
- 删除指定Chunk向量

FAISS只负责向量索引和相似度搜索，不负责文本切分、Embedding生成以及BM25关键词检索。

```text
Embedding Model
    ↓
Chunk Embedding
    ↓
  FAISS
    ↓
Top-K Chunk ID
```

## 2. FAISS在项目中的位置

在整个Retrieval Pipeline中，FAISS处于向量检索阶段：

```text
    User Query
        |
        ↓
   Query Embedding
        |
        ↓
┌───────────────┐
│     FAISS     │
│               │
│ IndexIDMap    │
│      ↓        │
│ IndexFlatIP   │
└───────┬───────┘
        |
        ↓
 chunk_id + score
        │
        ↓
 Hybrid Retrieval
        │
        ↓
       RRF
        │
        ↓
   CrossEncoder
```

本项目同时使用BM25进行关键词匹配，因此完整的混合检索流程为：
```text
                     Query
                       |
              ┌────────┴────────┐
              ↓                 ↓
       Query Embedding       Jieba 分词
              ↓                 ↓
            FAISS             BM25
              │                 │
              └────────┬────────┘
                       ↓
                      RRF
                       ↓
                 CrossEncoder
                       ↓
                  Final Results
```

## 3. Faiss核心概念

### 3.1 Embedding
Embedding 是将文本转换为固定多维度的数值向量，
在本项目中，Embedding使用"shibing624/text2vec-base-chinese"，对应向量维度为768维，
FAISS不负责生成Embedding，Embedding由独立的Embedding模型生成。
Embedding模型负责将文本转换为能够表达语义信息的向量，而FAISS负责对这些向量进行相似度搜索。

## 4. IndexFlatIP

项目代码
```text
base_index = faiss.IndexFlatIP(dim)
```

其中：
```text
Index
  ↓
 Flat
  ↓
 IP
```

### Index

表示 FAISS索引结构

### Flat

表示使用 Flat Index，进行精确搜索，需要与索引中的向量进行相似度计算。

```text
查询向量
   ↓
与所有向量进行相似度计算
   ↓
  排序
   ↓
 Top-K
```

优点：
- 实现简单
- 精准搜索
- 适合数据规模较小的场景

缺点；
- 数据量非常大时，搜索成本较高

### 

IP表示：
```text
Inner Product
```
即向量内积：
```text
A · B
=
A1AB1 + A2B2 + ... + AnBn
```
本系统已经在Embedding阶段对向量进行了L2 Normalize：
```text
||A|| = 1
||B|| = 1
```
那么：
```text
A · B = cosine_similarity(A, B)
```
向量内积对应余弦相似度。

## 5. IndexIDMap

### 5.1 为什么需要IndexIDMap

如果单独使用:
```text
faiss.IndexFlatIP(dim)
```
FAISS内部主要使用向量的位置进行标识，但是项目真正需要的是：
```text
MySQL Chunk ID
```
用于和MySQL Chunk主键进行对应。

因此项目使用：
```text
self.index = faiss.IndexIDMap(base_index)
```

### 5.2 add_with_ids

项目代码：
```text
self.index.add_with_ids(
    embeddings,
    ids
)
```

例如：
```text
Embedding A → Chunk ID 101
Embedding B → Chunk ID 102
Embedding C → Chunk ID 103
```

FAISS检索之后可直接返回chunk_ids，通过chunk_id找到对应Chunk。

## 6. Embedding数据格式

```text
embeddings = np.array(
    embeddings
).astype("float32")
```

### 6.1 为什么转换为NumPy
chunk内容在Embedding之后，结果为list或torch.Tensor，
但是FAISS往往需要NumPy数组，因此转换为
```text
np.array(...)
```

### 6.2 为什么使用float32
FAISS对输入数据有明确数据类型要求，项目统一转换为float32，
以此保证：
```text
Embedding
    ↓
NumPy ndarray
    ↓
 float32
    ↓
  FAISS
```

## 7. Embedding维度处理
```text
if len(embeddings.shape) == 1:
    embeddings = embeddings.reshape(1, -1)
```

如果向量输入为单个一维向量，例：
```text
[1,2,3]
```
但是FAISS添加向量时需要二维结构：
```text
[
    [0.1,0.2,0.3]
]
```
因此若条件成立，需要将向量进行reshape(1, -1)处理，
若条件不成立，初始即为二维向量，则不需要reshape。

## 8. 添加向量
```text
def add(
    self,
    embeddings,
    texts,
    chunk_ids
):
```

整个过程：
```text
Chunk
  │
  ├── text
  ├── chunk_id
  └── embedding
        │
        ↓
     VectorStore
        │
        ├──────────────┐
        ↓              ↓
      FAISS           BM25
```
FAISS部分：
```text
self.index.add_with_ids(
    embeddings,
    ids
)
```
最终建立Chunk ID和Embedding之间的映射。

## 9. 向量搜索
```text
distances, indices = self.index.search(
    query_embedding,
    top_k
)
```
输入：
```text
Query
 ↓
Query Embedding
 ↓
FAISS
```
最终返回distances与indices，
其中distances表示相似度分数，由于项目使用IndexFlatIP，因此distance越大相似度越高。
indices表示对应的Chunk ID，最终转换为：
```text
[
    {
        "chunk_id": 103,
        "score": 0.91,
        "source": "faiss"
    },
    ...
]
```

## 10. Top-K检索

对于检索出的chunk_ids，不会全部输出到hybrid Retrieval，
而是根据top_k的值，返回最相似的top_k个向量。
```text
 Query Embedding
      ↓
与所有 Chunk Embedding 计算相似度
      ↓
 按照相似度排序
      ↓
   取 Top-K
```

## 11. FAISS持久化

FAISS索引默认存在于内存中，如果程序关闭则索引消失，
因此需要对FAISS索引进行持久化。

### 11.1 保存FAISS
```text
faiss.write_index(
    self.index,
    f"{kb_path}/faiss.index"
)
```
流程：
```text
内存中的 FAISS Index
        ↓
   write_index()
        ↓
    faiss.index
```

### 11.2 加载FAISS
```text
self.index = faiss.read_index(
    index_path
)
```
流程：
```text
faiss.index
    ↓
read_index()
    ↓
内存中的 FAISS Index
```

## 12. VectorStore
项目并不会直接在业务代码中操作FAISS，而是通过VectorStore对其进行封装。
结构：
```text
VectorStore
│
├── self.index
│      ↓
│   FAISS
│
└── self.bm25
       ↓
     BM25
```

主要方法：
```text
add()
search()
save()
load()
delete()
```

## 13. VectorStoreManager
VectorStoreManager负责管理多个知识库对应的VectorStore，
```text
VectorStoreManager
│
├── KB A → VectorStore
├── KB B → VectorStore
└── KB C → VectorStore
```
使用：
```text
self.stores = {}
```
保存已经加载到内存中的VectorStore。
第一次访问：
```text
get_store()
    ↓
创建 VectorStore
    ↓
加载 faiss.index
    ↓
加载 bm25.pkl
    ↓
保存到 stores
```
后续访问：
```text
get_store()
    ↓
直接从 stores 获取
```
因此可以避免每次检索都重新读取磁盘

## 14. 多用户知识库隔离
由于项目支持用户级知识库，因此项目不能只使用kb_name作为缓存Key，
否则若是两个用户有着同名kb_name，会造成数据泄露的风险。
因此使用
```text
store_key = f"{owner_id}_{kb_name}"
```
从而保证不同用户的 VectorStore 缓存相互隔离。

## 15. 删除向量
```text
ids_array = np.array(
    chunk_ids
).astype("int64")

self.index.remove_ids(
    ids_array
)
```
流程：
```text
获取对应 Chunk ID
    ↓
Chunk ID
    ↓
FAISS remove_ids()
    ↓
删除对应向量
    ↓
删除 Document
```

## 16. 当前实现优点
- 结构简单，仅使用IndexIDMap、IndexFlatIP，无复杂索引结构
- FAISS与MySQL Chunk解耦
- 使用 IndexIDMap 保留业务 ID
- 支持持久化
- 支持多知识库

## 17. 当前局限与优化方向

### 17.1. IndexFlatIP 在数据量很大时效率有限

```text
faiss.IndexFlatIP(dim)
```
属于精确搜索，查询一个向量时，需要与大量向量进行相似度计算，
当Chunk数量达到百万级甚至更高时，搜索成本会明显增加。

后续可以根据数据规模选择：
- HNSW
- IVF
- PQ
- IVF + PQ
同时通过 Recall@K 等指标验证召回率变化。

### 17.2 当前使用内存缓存 VectorStore

VectorStoreManager 会将已经加载的 Store 保存在：
```text
self.stores = {}
```

因此知识库数量增加后，可能导致：
```text
VectorStore
    ↓
FAISS Index
    ↓
大量 Embedding 常驻内存
```

后续可考虑：
- LRU 缓存
- 限制同时驻留内存的知识库数量
- 不活跃知识库自动卸载
- 更专业的向量数据库


