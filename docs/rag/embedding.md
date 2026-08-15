# embedding

## 1. 模块概述

Embedding模块负责将文本转换为高维向量表示。
向量能够捕获文本语义信息，使语义相近的文本在向量空间中具有更高的相似度。
在RAG系统中，Embedding是FAISS向量检索的基础。

```text
    Text
     ↓
Embedding Model
     ↓
   Vector
     ↓
   FAISS   
```

## 2. 为什么使用Embedding

由于在检索系统中，用户问题中关键词和文本内容关键词有时并不完全一致，
```text
Query: 
怎么学习AI？
Chunk:
人工智能学习路线包括数学基础、机器学习和深度学习。
```
关键词匹配方式对于这种字面不一致的现象效果较差，往往无法分辨 AI ≈ 人工智能
但是当Embedding后，可以根据向量匹配得到AI与人工智能的语义对应关系，
因此能够实现同义词的语义检索优良的匹配效果。

## 3. Embedding加载
```text
get_embedding_model()
```

加载模型使用懒加载

流程：
```text
 Program Start
      ↓
embedding_model=None
      ↓
First Request
      ↓
  Load Model
      ↓
  Reuse Model
```

## 4. 双重检查锁
```text
if embedding_model is None:

    with embedding_lock:

        if embedding_model is None:
```
对于Embedding的加载，系统使用双重检查锁，避免在第一次加载后，
其他等待的线程再次加载模型，造成内存的浪费。
因此在lock锁释放以后，线程会再次进行模型是否为空的判断。
从而可以避免多线程重复加载模型。
```text
Thread A
   ↓
Load Model

Thread B
   ↓
Wait Lock
```

## 5. Embedding Cache
系统通过Embedding Cache缓存对应的Embedding结果，
在第一次提出问题时进行get失败，将结果上传到Cache，再次提出该问题则hit Cache，
避免重复调用Embedding模型。
```text
embedding_cache.get(text)
......
embedding_cache.set()
```
流程：
```text
        Text
         ↓
    Redis Cache
         ↓
        Hit
         | 
    +----+----+
    ↓         ↓
   Yes        No
    ↓         ↓
 Return     Encode
```
作用：
- 减少重复Embedding计算
- 降低响应时间
- 减少CPU/GPU消耗

## 6. Embedding生成

```text
model.encode(
    text,
    normalize_embeddings=True
)
```
Model使用:
```text
shibing624/text2vec-base-chinese
```
将输入的问题或者文本转换为高维向量，输出为768维高维向量，
向量中的每一个维度表示文本在语义空间中的特征表达，
模型通过训练学习不同文本之间的语义关系。

## 7. 向量归一化
模型在对文档进行encode时，使用向量归一化。
```text
normalize_embeddings=True
```
例如：
```text
原向量:
[3,4]
长度:
5
归一化:
[0.6,0.8]
```
归一化后向量长度=1

原因：
系统在FAISS模块中，使用了IndexFlatIP精确暴力内积搜索，
将每个query_embedding和chunk的Embedding进行内积计算，
当两个向量均完成L2归一化后，其内积结果等价于余弦相似度。
```text
Inner Product
=
Cosine Similarity
```

## 8. 在RAG中的位置

```text
Document
    ↓
Chunking
    ↓
Embedding
    ↓
FAISS Index
    ↓
Retriever
```

## 9. 批量Embedding

```text
get_embeddings()
```
该接口主要用于文档上传阶段，对多个Chunk进行批量向量化处理。
输入：
```text
[
 "chunk1",
 "chunk2",
 "chunk3"
]
```

输出：
```text
[
 [..],
 [..],
 [..]
]
```

效果：
- 减少模型推理次数
- 提高上传效率

## 10. 当前实现优点
- 模型单例化
- 懒加载
- 双重检查锁
- Embedding结果缓存，避免重复推理
- 向量归一化
- 支持批量Embedding

## 11. 优化方向

### 11.1 批量缓存

```text
get_embeddings()
```
没有存入缓存，未来可以进行Batch Cache，进一步提高效率

### 11.2 多Embedding模型
当前使用单模型进行Embedding，后续可使用
```text
BGE
GTE
text2vec
```
支持切换

