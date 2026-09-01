# AI知识库助手系统架构设计

## 1. Overview

AI知识库助手采用模块化 RAG 架构，

系统主要由以下模块组成：

- API 接入层
- 业务服务层
- 文档处理层
- 数据存储层
- 检索层
- 缓存管理层
- LLM生成层

系统支持多知识库隔离，每个知识库拥有独立的：
- 数据目录
- FAISS索引
- BM25索引
避免不同知识库之间的数据和检索结果互相污染。

## 2. 整体架构

### 用户上传文档
```text
用户上传文件
    ↓
Upload API
    ↓
Document Pipeline
    ↓
文档解析
    ↓
Chunk切分
    ↓
Embedding生成
    ↓
VectorStore存储
    ↓
MySQL + FAISS + BM25
```

### 用户查询流程
```text
用户问题
    ↓
API接口层
    ↓
user Authentication
    ↓
Chat Service
    ↓
Retriever检索
    ↓
Context构建
    ↓
LLM生成回答
    ↓
 返回结果
```

## 3. Software Architecture

### API Layer
- HTTP接口
- 请求参数接收
- 请求参数处理

位置：app/api/


### Service Layer
- 知识库管理
- 业务流程
- 调用底层模块

位置：app/services/

### Document Pipeline
负责：
- 文件解析
- 文本切分
- Metadata生成
- Embedding生成

### Knowledge Base Layer
负责：
- 多知识库管理
- 数据隔离
- 生命周期管理

核心组件：
- VectorStoreManager

### Retriever Layer
- 负责召回相关chunks
- 整合FaissRetriever,BM25Retriever,HybridRetriever,Reranker

位置：app/retriever/


### Storage Layer

系统采用两类存储。

#### 业务数据存储
MySQL保存：
- KnowledgeBase
- Document
- Chunk
- Conversation
- Message
- Task
- User

代码位置：
```text
app/database/
app/models/
app/crud/
```

#### 索引存储
用于RAG检索：
- FAISS向量索引
- BM25关键词索引

代码位置：
```text
app/vector_store/
app/bm25/
```

## 4. Multi Knowledge Base Architecture
系统通过 VectorStoreManager 管理不同知识库对应的 VectorStore。
```text
            VectorStoreManager
                    |
            +-------+------------+
            |                    |
        copper_based          medical
        VectorStore          VectorStore
            |                    |
        +---+---+            +---+---+ 
        |       |            |       |
      FAISS    BM25         FAISS    BM25
```

不同知识库之间：

- MySQL数据隔离
- FAISS索引隔离
- BM25索引隔离

避免知识库之间检索污染。


## 5. Cache Management

### 5.1 内存缓存

为了避免每次查询重新加载索引，
系统使用 VectorStoreManager 缓存 VectorStore实例。
当知识库发生变化时：
- 上传文档
- 删除文档
- 删除知识库
系统主动失效对应缓存

### 5.2 Redis缓存

Redis用于：
- Embedding缓存
- Retrieval结果缓存
- 异步任务状态

当知识库发生变化时：
- 上传文档
- 删除文档
- 删除知识库

系统主动清理Retrieval缓存

以上缓存均保证：
- Database
- File System Index
- Memory Cache

三者状态一致。

## 6. System Data Flow

### 6.1 Document Processing Flow

```text
User Upload
    ↓
Upload API
    ↓
Create Task
    ↓
Celery Worker
    ↓
Document Parser
    ↓
Chunk Splitter
    ↓
 Embedding
    ↓
VectorStore
    |
    +--- Faiss Index
    |
    +--- BM25 Index
    |
    ↓
Database Upload
```

### 6.2 Query Flow
```text
user Query
    ↓
 API Layer
    ↓
Authentication   
    ↓
 Chat Service
    ↓
Load Conversation History
    ↓
Hybrid Retriever
    ↓
 RRF Fusion
    ↓
CrossEncoder Rerank
    ↓
Prompt Construction
    ↓
   LLM
    ↓
Streaming Response
    ↓
Save Message
```

## 7. 技术栈
后端：
- FastAPI
- SQLAlchemy
- Pydantic

数据库：
- MySQL

任务队列：
- Celery
- Redis

RAG：
- SentenceTransformer
- FAISS
- BM25
- CrossEncoder

模型：
- LLM API

部署：
- Docker Compose

