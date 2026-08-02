# System Architecture

## 1. Overview

AI知识库助手采用模块化 RAG 架构，
由 API 接入层、业务服务层、文档处理层、数据存储层、检索层、缓存管理层和生成层组成。

系统支持多知识库隔离，每个知识库拥有独立的数据目录、FAISS索引以及BM25索引。

用户上传文档：

File Upload

↓

Document Pipeline

↓

Chunk Processing

↓

Database + Retriever Index


用户查询：

Query

↓

Retriever

↓

Context Construction

↓

LLM Generation


## 2. 软件模块架构

### API Layer
- HTTP接口
- 请求参数处理

位置：app/api/


### Service Layer
- 知识库管理
- 业务流程
- 调用底层模块

位置：app/service/

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

### Retriever Layer
- 负责召回相关chunks
- 整合FaissRetriever,BM25Retriever,HybridRetriever,Reranker

位置：app/retriever/


### Storage Layer
- MySQL + FAISS + BM25管理

位置：
    app/database/
    app/vector_store/
    app/bm25/

### MySQL
- KnowledgeBase
- Document
- Chunk
- Metadata

位置：app/database/
     app/models/
     app/crud/


## 3. Multi Knowledge Base Architecture
系统通过 VectorStoreManager 管理不同知识库对应的 VectorStore。

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

不同知识库之间：

- MySQL数据隔离
- FAISS索引隔离
- BM25索引隔离

避免知识库之间检索污染。


## 4. Cache Management

为了避免每次查询重新加载索引，
系统使用 VectorStoreManager 缓存 VectorStore实例。
当知识库发生变化时：
- 上传文档
- 删除文档
- 删除知识库
系统主动失效对应缓存，
保证 Memory Cache 与 File System Index 状态一致。
