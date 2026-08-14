AI Knowledge Base Architecture Notes


## 为什么需要 VectorStore？
如果没有封装，faiss_index,texts,metadata,bm25 将会分散在不同的地方，
会导致：数据管理困难、多知识库无法隔离、代码复用困难。
因此设计 VectorStore，并且一个 VectorStore 对应一个知识库

## 为什么需要 Manager？
对于单知识库，无需使用 Manager 对实例进行管理，
但是多知识库：copper_base,medical,legal，这些都需要Faiss，BM25，metadata。
如果不使用 Manager，会出现: 数据混合、index 覆盖、查询错误
因此使用 VectorStoreManager 对多个知识库进行管理，通过 kb_name 找到对应的实例

## 为什么 BM25 放在 VectorStore 内？
因为 BM25 和 FAISS 属于同一个知识库的数据，
必须保证它们之间的对应一致，如果使用 BM25 独立管理，容易出现数据错位

## 一次查询经过哪些模块？
User Query
    ↓
FastAPI
    ↓
Retriever
    ↓
KnowledgeManager
    ↓
VectorStore
    ↓
Faiss semantic search
    +
BM25 keyword search
    ↓
Deduplication
    ↓
CrossEncoder Rerank
    ↓
Prompt Builder
    ↓
Qwen
    ↓
Answer + Source


## 数据生命周期
### 上传
PDF/TXT
↓
Parser
↓
Chunk
↓
Embedding
↓
VectorStore.add()
↓
Faiss 保存
↓
BM25 保存
↓
texts.pkl 保存


### 查询
query
↓
加载对应 kb
↓
retrieve
↓
生成答案


## Retrieval

### 4.1 FAISS Semantic Retrieval

#### Q1. 为什么 Query 不能直接进入 FAISS？

Query 本身是文本，FAISS 接收的是向量。
因此需要先通过 Embedding Model 将 Query 编码为向量，
再转换为 FAISS 所要求的数据格式（如 float32）。

#### Q2. Embedding 的 768 维是什么意思？

表示文本被映射到 768 维向量空间中的一个点。
这 768 个维度共同表示文本的语义特征，
并不是对应 768 个词。

#### Q3. 为什么使用 IndexFlatIP？

IndexFlatIP 使用 Inner Product 进行精确搜索。
项目中的 Embedding 向量经过 L2 Normalize 后：
A · B = cosine_similarity(A, B)
因此可以使用 Inner Product 实现 Cosine Similarity 检索。

#### Q4. D 和 I 分别是什么？

index.search(query_vector, k) 返回 D 和 I。

D：Inner Product 得分，在本项目中可理解为相似度分数。
I：FAISS 中对应向量的 ID。

由于项目使用 IndexIDMap，并将 Chunk ID 作为向量 ID，
因此 I 可以直接用于定位 MySQL 中的 Chunk。


#### Q5. 为什么使用 IndexIDMap？

FAISS 的向量需要与业务数据库中的 Chunk 建立对应关系。

IndexIDMap + add_with_ids() 可以使：

FAISS Vector ID = MySQL Chunk ID

从而通过 FAISS 检索结果直接查询对应 Chunk。


#### Q6. IndexFlatIP 是近似搜索吗？

不是。

IndexFlatIP 属于 精准复杂搜索，会对 Query 与所有向量计算内积，
然后选出 Top-K。

优点是结果精确，缺点是数据规模增大后计算成本上升。
