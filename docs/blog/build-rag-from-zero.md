# 从 0 到 1 构建企业级 RAG 知识库系统：架构设计与工程实践

## 1. 项目背景

随着企业数字化建设的发展，企业在生产、研发、运营过程中，积累了大量的企业内部知识，
这些知识往往存在于PDF、Word、技术文档等非结构化数据中，

由于缺少有效的知识管理方式，企业员工在面对海量文档时，
难以快速定位所需信息，降低了知识利用效率。

与此同时，传统的大语言模型虽然具备强大的自然语言理解和生成能力，
但是无法直接访问企业私有知识，且由于大模型本身的上下文长度限制以及成本限制，
将大量文档同时传递给大模型进行阅读查找是不现实的，
因此本文设计并实现了一个基于检索增强生成（Retrieval-Augmented Generation, RAG）的企业知识库问答系统。

该系统通过文档解析、文本切分、向量化存储、混合检索以及大模型生成，
实现企业私有知识的智能检索与问答。

项目目标：
- 支持多知识库管理，实现不同知识域隔离
- 支持文档上传、解析和自动切分
- 支持向量检索与关键词检索的混合召回
- 支持CrossEncoder Rerank优化检索排序
- 支持LLM基于检索结果生成答案
- 提供Recall@K、MRR等检索效果评估指标
- 支持检索结果来源追踪，提高系统可解释性

## 2. 系统整体架构

                                 User
                                  |
                             Vue3 Frontend
                                  |
                            FastAPI Backend
                                  |
                      +-----------+-----------+
                      |                       |
                    Upload                 Query
                      |                       |
              Document Pipeline          Chat Pipeline
                      |                       |
              PDF/TXT Parsing                |
                      |
              Chunk Split
                      |
              Embedding Generation
                      |
                      |
               Database Layer
                      |
             +--------+--------+
             |                 |
    Knowledge Base A   Knowledge Base B
             |                 |
       MySQL Metadata   MySQL Metadata
             |
    VectorStoreManager
             |
         +---+----------------+
         |                    |
     FAISS Index        BM25 Index
         |
         |
    Hybrid Retrieval
         |
    Metadata Filter
         |
    Deduplication
         |
    CrossEncoder Rerank
         |
    Context Construction
         |
      Qwen LLM
         |
    Answer + Source Tracking


## 3. 技术选型

### Backend

FastAPI:
负责REST API、业务逻辑和异步接口

### Hybrid Retrieval

FAISS:
高维向量相似度搜索

BM25:
关键词匹配，提升专业术语召回能力

### Rerank

CrossEncoder:
对召回结果进行精排

### Database

MySQL:
保存知识库 + 文档 + Chunk 结构化数据

FAISS向量存储

BM25关键词存储

采用MySQL + Vector Index混合存储架构。

## 4. 文档处理流程

PDF/TXT
 ↓
Parser
 ↓
Text Split
 ↓
Chunk
 ↓
MySQL生成chunk_id
 ↓
Embedding
 ↓
FAISS建立索引
 ↓
BM25建立索引


## 5. 知识库管理

为了根据文档主题的不同，实现不同业务之间的数据隔离，
系统设计了多知识库管理机制，实现不同知识库之间的隔离。

每个知识库拥有独立的：
- 文件目录
- FAISS Index
- BM25 Index
- MySQL Metadata

系统通过VectorStoreManager，
根据kb_name管理不同知识库对应的向量

knowledgeBase
      |
      |
   Document
      |
      |
    Chunk

在查询过程中，用户输入kb_name，定位到对应的VectorStore，
通过不同的对象对当前知识库进行检索，从而完成知识库隔离


## 6. 检索系统设计

## 7. LLM问答流程

## 8. 系统评估

## 9. 遇到的问题和解决方案

### 知识库删除时外键约束异常
在实现知识库删除功能时，发现直接删除 KnowledgeBase 会触发 MySQL 外键约束异常，

KnowledgeBase 和 Document 存在一对多的关系，即：

    KnowledgeBase
        |
        |
    Document 
        |
        |
      Chunk

当 KnowledgeBase 下仍然存在 Document 记录时，MySQL不允许删除父表数据。

#### 原因分析
在删除流程中，部分Document可能不存在对应的Chunk，
原逻辑：
```
if not chunk_ids:
    return False
```
当文档不存在Chunk时，删除流程直接提前终止，导致Document删除流程被跳过，
Document没有成功删除，KnowledgeBase 删除时触发外键约束异常

#### 解决方案
```
if not chunk_ids:

    document_crud.delete_document(
        db,
        doc_id
    )

    return True
```
保证在无Chunk的情况下依然可以成功删除Document

#### 工程收益
通过改正该数据库外键问题，确保了 Document 与 KnowledgeBase外键关系正确维护，
删除流程可以支持空 Chunk 文档，提升知识库管理功能的稳定性。

#### 设计总结
知识库删除涉及到了多组数据的删除，而非简单的数据库delete操作，
其中涉及了：
- MySQL业务数据
- Chunk数据
- Document存储
- FAISS向量索引
- BM25关键词索引

当多个存储层需要进行协同操作时，需要考虑数据一致性问题，
因此在进行删除操作时，应当按照依赖关系来执行，防止出现脏数据。


### VectorStore缓存导致索引数据不一致问题
在实现多知识库检索功能时，发现知识库更新或删除后，检索结果有时仍然包含旧数据。
经过排查发现，在删除操作后，FAISS和BM25索引已经更新或删除，问题并非来自FAISS和BM25本身，
而是由于引入了VectorStoreManager缓存后，内存中的VectorStore对象状态
与磁盘索引文件不一致导致，也就是在删除知识库之后，没有对缓存进行处理。


      Memory Cache

    VectorStoreManager
            |
            |
        VectorStore
            |
            |
        FAISS Index
        BM25 Store

#### 原因分析
为了避免每次查询都重新加载FAISS索引和BM25数据，以及更方便的进行多知识库管理，
系统使用了 VectorStoreManager 对 VectorStore 对象进行缓存。

首次访问知识库：


    get_store(kb_name)
        
            ↓

     创建 VectorStore

            ↓

          load()

            ↓

      读取 faiss_index

            ↓

        加载BM25数据

            ↓

         保存到缓存
后续查询复用缓存：

    cache["knowledge_base"]
    
            |
            |
        VectorStore
    
            |
            |
        FAISS Index
        BM25 Store

执行知识库删除之后，原流程只修改数据库和磁盘文件，缓存仍然存在。


    Memory Cache
    VectorStore

        |
        |

     FAISS旧索引
     BM25旧数据
已删除知识库对应的旧 VectorStore 对象仍然可以被访问，内存索引与磁盘索引不一致

#### 解决方案
采用 Cache Invalidation（缓存失效）机制。
在进行kb_delete之后，主动清理对应知识库缓存。
增加功能：
```python
def remove_store(
        self,
        kb_name
):
    self.stores.pop(
        kb_name,
        None
    )
```

知识库删除时，由于删除过程需要依赖VectorStore 中的 FAISS/BM25 状态，因此不能提前删除缓存。
由于删除 Document 时需要依赖 KnowledgeBase 下的文档关系，因此数据库中的 KnowledgeBase 记录需要在相关资源清理完成后删除。
因此最终删除流程为：


    删除Document

        ↓

     删除Chunk

        ↓

    更新/删除FAISS索引
    更新/删除BM25索引

        ↓

    删除本地索引文件

        ↓

    清理VectorStore缓存

        ↓

    删除KnowledgeBase记录


#### 工程收益
通过使用缓存失效机制：
- 保证内存缓存与磁盘索引数据一致
- 避免知识库删除后仍然存在旧检索缓存结果
- 支持知识库动态更新

#### 设计总结
RAG系统不仅含有数据库、磁盘存储层，在一定条件下还存在缓存存储层。
MySQL: Document + Chunk
File System: FAISS Index + BM25 Index
Memory: VectorStore Cache
当多个存储层同时维护同一业务数据时，需要考虑数据一致性问题。
因此，对于涉及索引变化的操作，需要进行：
- 新增文档
- 删除文档
- 删除知识库
- 更新索引


### 模型生命周期管理与推理性能优化

在RAG系统中，Embedding模型和CrossEncoder Reranker模型属于核心推理组件，
在此期间需要占用大量的显存，时间开销大。
#### 1. Lazy Loading 与 Thread-safe Initialization

##### 原因分析
在初始实现中；

Embedding模型：
```
model = SentenceTransformer(
    EMBEDDING_MODEL
)
```
在程序启动或模块首次导入时加载模型。

CrossEncoder模型：
```
model = AutoModelForSequenceClassification.from_pretrained(...)
```
初始实现中，在Reranker模块初始化阶段加载。

这种方式在实现上比较简单，但是却存在着以下问题：
- 服务启动时间过长
- 即使没有请求也会占用内存/GPU资源
- 多线程时可能会出现重复初始化等异常

##### 解决方案

为了优化模型生命周期管理，系统采用：
- Lazy Loading
- Thread-safe Initialization

系统改为仅首次使用时加载模型，
降低资源占用、提升服务启动速度。

      请求
 
       ↓

    调用Embedding/Reranker

       ↓

    检查模型实例

       ↓

     加载模型

       ↓

    缓存模型对象

核心逻辑：
```
if model is None:

    with lock:

        if model is None:

            model = load_model()
```

通过双重检查锁，保证：
- 模型只加载一次
- 并发请求不会重复初始化

#### 2. CrossEncoder Batch Inference优化

初始Rerank流程：

    Query + Document1
            ↓
           推理

    Query + Document2
            ↓
           推理
每个query-document二元组单独进行模型推理

优化后：

    [
    (Query, Document1),
    (Query, Document2),
    (Query, Document3)
    ]
    
              ↓
    
    Batch Tokenization
    
              ↓
    
    Batch Inference
通过批量推理减少模型调用次数，提高Reranker排序效率。

#### 工程收益
通过模型生命周期优化：
- 降低服务启动时间
- 减少无效模型加载
- 提高并发环境稳定性

使RAG系统具备更接近生产环境的模型管理能力


## 10. 后续优化