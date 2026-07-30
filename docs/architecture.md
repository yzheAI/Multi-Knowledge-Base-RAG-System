# System Architecture

## 1. Overview

AI知识库助手采用模块化 RAG 架构，
由 API 接入层、业务服务层、文档处理层、数据存储层、检索层和生成层组成。

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
- 业务流程
- 调用底层模块

位置：app/service


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
