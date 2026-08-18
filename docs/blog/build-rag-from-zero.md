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


## 6. 多用户知识库系统设计

为了支持企业内部的多用户使用场景，系统增加了用户认证与权限隔离机制，
用户需要先取得token才能使用知识库系统进行问答。

不同用户使用独立的知识库空间，避免不同用户之间的数据访问和上下文污染，
防止知识库隐私泄露。

系统整体结构：

        User
    
          |

    KnowledgeBase

          |

       Document

          |

        Chunk

其中：
    KnowledgeBase 通过 owner_id 关联用户

    User
     |
     | 1:N
     |
    Knowledge

每个用户可以创建管理多个知识库，
但是各用户只能访问自己的知识库。

### 6.1 用户认证

系统采用JWT实现用户身份认证。

登录流程：

        User
         ↓
     输入用户密码
         ↓
     密码Hash校验
         ↓
    生成JWT Token
         ↓
    客户端获取Token

后续再次登录：
    
    用户携带Token
        ↓
     解析JWT
        ↓
    获取user_id
        ↓
      权限校验

### 6.2 知识库权限隔离

为了防止用户能够访问其他用户知识库，造成数据泄露或丢失，
将所有的知识库操作都绑定当前用户身份(user_id)。

查询知识库：user_id + kb_name 用于定位当前用户拥有的知识库。

对于上传、删除、查询知识库：
使用数据库验证 KnowledgeBase.owner_id == current_user.id,
对符合条件的kb进行操作，否则拒绝访问

### 6.3 多用户上下文记忆隔离

在每个聊天对话框中，如果不同的用户共享同一个Conversation Memory,
会出现不同用户之间记忆数据共享的情况，导致历史上下文污染。

因此系统设计MemoryManager管理不同用户的聊天上下文。

在获取当前上下文信息时，首先通过(user_id,kb_name)定位到符合条件的历史上下文。
例如：

    admin1 + copper_based
            |
         历史记录   

    admin2 + medical
            |
        历史记录2

不同用户之间聊天历史信息进行隔离

### 6.4 Container统一管理核心组件

系统通过Container统一管理全局服务组件
- VectorStoreManager
- Retriever
- Reranker
- MemoryManager

避免业务代码重复创建对象，服务启动时Container仅创建一次，
且组件实例在当前服务进程生命周期内保持，业务模块通过Container获取已有组件。


## 7. Query Rewrite 与检索系统设计
### 7.1 Query Rewrite

在多轮对话场景中，用户后续问题通常会依赖前文的上下文，
例如：

```text
User：铜基复合材料是什么？

Assistant：......

User：它为什么适合用于电子散热器？
```
在后续的问题中，可能会将主语用其他代词代指，
然而在retrieval的时候，“它”缺少明确的代指对象。
如果直接将原始Query送入Retrieval，会导致检索结果受到影响。
因此在进行RAG检索流程之前，系统增加Query Rewrite模块，
利用Conversation History将原始问题根据上下文历史改写为完整的检索Query
例如：
```text
原始Query：
它为什么适合用于电子散热器？

Rewrite Query：
铜基复合材料为什么适合用于电子散热器？
```
但是系统并不是对所有Query进行Rewrite，
而是通过适当的规则判断当前Query是否可能存在上下文依赖。
```python
def need_rewrite(query):
    keywords = [
        "它",
        "这个",
        "那个",
        "上述",
        "前面",
        "该"
    ]

    return any(
        keyword in query
        for keyword in keywords
    )
```
如果Query不含有以上代指词，则直接进行Retriever，
避免进行不必要的LLM调用，降低系统延迟和调用成本。

如果需要对Query进行Rewrite，则结合Conversation History调用LLM：
```text
Conversation History
        +
    Base Query
        ↓
    Qwen Rewrite
        ↓
   Rewrite Query
        ↓
 Hybrid Retrieval
```
Rewrite阶段只负责补全Query语义，不直接回答用户问题。


### 7.2 Hybrid Retrieval
系统采用 FAISS + BM25 双路召回方式。

FAISS负责语义相关性检索，
BM25负责关键词匹配，
通过RRF融合两个Retriever的排序结果，
随后交给CrossEncoder进行精排。

### 7.3 CrossEncoder Rerank
FAISS和BM25完成召回之后，会产生大量的Chunk，
然而：
- FAISS只考虑向量相似度
- BM25只考虑关键词匹配
二者无法单独准确衡量Query与Chunk之间的语义相关性，
因此系统引入CrossEncoder作为下阶段的排序器。


### 7.4 Redis Cache Optimization
在RAG系统中，Embedding计算和Retriever检索过程属于高频调用模块，
但是对于重复问题，如果每次都重复计算Embedding然后执行Retriever，
会大大增加系统的响应时间和模型推理开销。
因此系统引入Redis作为缓存层，以此减少重复计算，提高系统性能。

#### 1. Embedding Cache
Embedding生成过程设计SentenceTransformer模型推理，
对于相同的Query，Embedding结果保持一致，因此采用：
```python
def demo(kb_name, query):
    cache_key = f"embedding:{query}"
```
首先查询Redis：
```text
Redis
├── Hit
│      ↓
│   返回Embedding
│
└── Miss
       ↓
   模型推理
       ↓
   写入Redis
```

#### 2. Retrieval Cache
Embedding完成后，Hybrid Retrieval仍然需要大量计算：
```text
FAISS Search
      +
BM25 Search
      +
RRF Fusion
      +
Rerank
```
由于召回过程计算成本大，因此系统进一步缓存Retriever结果，
```python
def demo(kb_name, query):
    cache_key = f"retrieval:{kb_name}:{query}"
```
缓存内容：
- chunk_id
- score
- metadata

查询流程：
```text
User Query
      |
  Redis Check
      |
 +----+----+
 |         |
Hit      Miss
 |         |
返回结果   Retriever
              |
          Cache Result
```
对于高频问题，
可以直接返回检索结果，
避免重复执行FAISS、BM25以及Rerank流程。

#### 工程收益
Redis缓存机制带来了：
- 降低Embedding模型调用次数
- 减少FAISS与BM25重复检索
- 降低CrossEncoder推理开销
- 提高系统响应速度

最终效果：
```text
User Query
      |
 Query Rewrite
      |
 Redis Cache
      |
 +----+----+
 |         |
Hit      Miss
 |         |
直接返回  Hybrid Retrieval
              |
         CrossEncoder
              |
           Cache
              |
         Return Answer
```

## 8. 异步文档处理架构

### 8.1 问题分析
在RAG系统中，文档上传不仅仅是保存文件，还需要执行以下复杂操作：
```text
PDF/TXT解析
      ↓
Chunk切分
      ↓
Embedding生成
      ↓
FAISS构建
      ↓
BM25构建
```
其中Embedding生成涉及了深度学习模型推理，对于大型文档耗时较多。
如果直接在HTTP请求中执行，会导致以下问题：
- 请求超时
- 用户等待时间长
- API线程长时间阻塞

### 8.2 Celery + Redis方案
基于以上问题，系统采用：
```text
 FastAPI
    |
Redis Broker
    |
Celery Worker
```
上传流程：
```text
User Upload
      |
 FastAPI API
      |
 创建Task记录
      |
 发送Celery任务
      |
 立即返回task_id
      |
 ----------------
      |
 Celery Worker
      |
 Document Pipeline
      |
 更新任务状态
```
FastAPI仅负责接受请求，耗时任务由Worker后台执行，避免阻塞API服务。

### 8.3 任务状态管理
系统设计Task数据表
```text
Task

id
user_id
filename
status
error_message
created_at
```
用户可通过：Get/tasks/{task_id} 查询处理状态

### 工程收益
引入异步任务架构后：
- 上传接口迅速返回
- 避免长时间HTTP阻塞
- 提高系统并发能力
- 支持大规模文档处理
- 提高用户体验

整体架构：
```text
User
 |
Upload
 |
FastAPI
 |
Redis Broker
 |
Celery Worker
 |
Document Pipeline
 |
FAISS/BM25
 |
MySQL
```

## 9. LLM问答流程

## 10. 系统评估

### 10.1 Retriever Evaluation

实验结果：

| Retriever | Recall@1 | Recall@3 | Recall@5 | MRR    |
|-----------|----------|----------|----------|--------|
| FAISS     | 25.86%   | 43.10%   | 50.00%   | 35.26% |
| BM25      | 48.28%   | 74.14%   | 82.76%   | 60.92% |
| Hybrid    | 63.79%   | 86.21%   | 87.93%   | 74.28% |

### 10.2 Query Rewrite Evaluation

为了验证Query Rewrite是否能够改善多轮对话场景下的检索效果，
构建包含上下文依赖问题的JSON数据集。

实验采用相同的Hybrid Retriever,
仅改变输入Retriever的Query，从而比较Retriever前后的检索效果。

实验结果：

| Method        | Recall@1 | Recall@3 | Recall@5 | MRR    |
|---------------|----------|----------|----------|--------|
| Base Query    | 43.10%   | 58.62%   | 65.51%   | 52.21% |
| Query Rewrite | 58.62%   | 84.48%   | 86.20%   | 70.54% |

```markdown
从实验结果来看，Query Rewrite能够明显提升上下文依赖Query的检索效果。

Recall@1从43.10%提升至58.62%，
Recall@3从58.62%提升至84.48%，
Recall@5从65.51%提升至86.20%，
MRR从52.21%提升至70.54%。

其中Recall@5提升超过20个百分点，
说明Query Rewrite能够有效降低省略主语、指代等上下文依赖问题
对Retriever召回能力造成的影响。
```
## 11. 遇到的问题和解决方案

### 11.1 知识库删除时外键约束异常
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


### 11.2 VectorStore缓存导致索引数据不一致问题
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


### 11.3 模型生命周期管理与推理性能优化

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


## 12. 后续优化