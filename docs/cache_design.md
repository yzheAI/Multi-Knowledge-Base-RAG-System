# Cache Design

## 1. 模块概述

AI知识库助手中存在大量的重复计算和重复数据读取的操作，例如：
- Faiss索引加载
- BM25索引加载
- Retrieval结果查询
- Query Embedding生成

如果每次请求都重新计算或者读取磁盘，会导致系统响应速度下降。

因此系统设计了多层缓存机制：
- Memory Cache
- Redis Cache

用于提高系统的响应速度，并保证数据更新后的缓存一致性。

## 2. 缓存架构

```text
        User Query
            |
            ↓
       Chat Service
            |
            ↓
      Retrieval Cache(Redis)
     +------+------+
     |命中          |未命中
     ↓             ↓
   返回结果     VectorStoreManager
                   |
                   ↓
               Memory Cache
                   |
                   ↓
             FAISS + BM25 Index
```
系统缓存分为两层：

| 缓存           | 存储位置       | 作用                     |
|--------------|------------|------------------------|
| Memory Cache | Python进程内存 | 缓存VectorStore实例        |
| Redis Cache  | Redis      | 缓存检索结果和Query Embedding |

## 3. Memory Cache设计

### 3.1 使用目的

FAISS和BM25索引文件存储在磁盘。

如果每次查询：
```text
Query
  ↓
加载FAISS文件
  ↓
加载BM25文件
  ↓
执行检索
```
会产生大量的IO。
因此系统使用VectorStoreManager缓存已经加载的VectorStore对象。

### 3.2 缓存内容

Memory Cache保存：
```text
knowledge_base_id
    ↓
 VectorStore
    ↓
  Faiss Index
  BM25 Index
  Metadata
```

### 3.3 查询流程

第一次查询：
```text
Query
  ↓
VectorStoreManager
  ↓
self.store中不存在
  ↓
磁盘加载FAISS/BM25
  ↓
保存到Memory Cache
  ↓
执行检索
```

第二次查询：
```text
Query
  ↓
VectorStoreManager
  ↓
Memory Cache命中
  ↓
直接检索
```
避免重复加载索引。

## 4. Redis Cache设计
Redis主要用于存储跨进程共享的数据。

### 4.1 Retrieval Cache

用户查询相同问题时，无需重新执行：
- Embedding
- FAISS搜索
- BM25搜索
- RRF融合

流程：
```text
Query
  ↓
生成cache key
  ↓
查询Redis
  ↓
命中
  ↓
返回历史结果
```

### 4.2 Embedding Cache

Query在进入Retriever之前，需要通过Embedding模型转换为向量表示。

由于Embedding模型推理存在一定计算开销，
对于相同文本的重复Embedding请求，可以直接复用历史计算结果。

Redis无法直接保存numpy.ndarray，
因此系统将Embedding向量转换为list后进行JSON序列化，
读取时再转换回numpy数组。

流程：
```text
            Query Text
                |
                ↓
            生成Hash Key
                |
                ↓
            查询Redis
           +----+----+
           |         |
          命中      未命中
           |         |
           ↓         ↓
返回Embedding Vector Query Text
                     ↓
                 Query Text
                     |
                     ↓
                 Embedding Model
                     |
                     ↓
                 生成Vector
                     |
                     ↓
                 保存Redis
```

## 5. Cache Key设计

不同类型的缓存使用不同Key。

### Retrieval Cache
格式：
```text
f"{self.PREFIX}"
f"{owner_id}:"
f"{kb_id}:"
f"{query_hash}"
```
其中：
- owner_id保证用户隔离
- kb_id保证知识库隔离
- query_hash避免key过长

### Embedding Cache
```text
embedding:{query_hash}
```

## 6. Cache Invalidation
缓存最大的问题是数据更新后缓存过期。
用户上传新文档：
```text
新增Chunk
    ↓
FAISS更新
    ↓
旧Retrieval Cache失效
```
因此系统设计主动缓存失效机制。

### 6.1 触发条件
上传文档
```text
Upload
   ↓
Update Index
   ↓
remove VectorStore Cache
   ↓
Delete Retrieval Cache
```

删除文档
```text
Delete Chunk
    ↓
Update Index
    ↓
remove VectorStore Cache
   ↓
Delete Retrieval Cache
```

删除知识库
```text
Delete KnowledgeBase
    ↓
Remove All Cache
```

## 7. 数据一致性
系统需要保证
```text
MySQL 
+
FAISS/BM25 Index
+
Cache
```
三者状态一致，如果在新增Chunk时，只在MySQL进行了新增，FAISS中还是旧Index，
Redis中还是旧Retrieval结果，会导致检索不到最新文档，因此数据变化后：
```text
Database Update
↓
Index Update
↓
Cache Invalidation
```
保证数据一致。

## 8. 优化方向

### 8.1 LRU缓存

限制Memory Cache大小：

最多保存N个VectorStore，防止知识库数量过多导致内存增长。

### 8.2 Redis TTL

设置自动过期：
```text
retrieval cache:
TTL = 30min
```
避免长期保存无效数据。

## 9. 总结
AI知识库助手采用两级缓存架构：
- Memory Cache缓存VectorStore实例，减少FAISS/BM25索引加载时间
- Redis缓存检索结果和Query Embedding，提高系统响应速度

同时通过Cache Invalidation机制，在知识库数据发生变化时主动清理缓存，保证：
- MySQL数据
- 向量索引
- 缓存结果
三者保持一致。
该缓存设计提升了RAG系统查询效率，并增强了系统在多知识库场景下的稳定性。
