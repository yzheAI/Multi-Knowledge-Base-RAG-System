# v2_rag.md

## 1. Overview

V2版本在基础 RAG 系统基础上进行了工程化升级，
实现从简单向量检索系统到多知识库、数据库驱动的完整 RAG Pipeline。

主要升级包括：

- Multi Knowledge Base
- MySQL Metadata and Chunk Persistence
- FAISS Vector Retrieval
- Hybrid Retrieval
- BM25 Key Retrieval
- CrossEncoder Rerank
- Retriever Evaluation
- Docker Container Deployment
- Retriever Interface Abstraction

整体实现从简单向量检索升级为完整 RAG Pipeline。

## 2. Overall Architecture
```mermaid
graph TD
A[User Query] --> B[FastAPI Chat API]

B --> C[RAG Service]

C --> D[Knowledge Base Selector]

D --> E[VectorStoreManager]


E --> F[Load VectorStore Instance]


F --> G1[FAISS Index]
F --> G2[BM25 Index]


C --> H[Query Processing]


H --> I1[SentenceTransformer Embedding]

H --> I2[Jieba Tokenization]


I1 --> G1
I2 --> G2


G1 --> J1[Semantic Retrieval]

G2 --> J2[Keyword Retrieval]


J1 --> K[Hybrid Merge]

J2 --> K


K --> L[Deduplication]

L --> M[CrossEncoder Reranker]

M --> N[Top-k Context]


N --> O[Qwen LLM]

O --> P[Answer + Source Tracking]



%% Database

Q[MySQL Database]

Q --> Q1[Knowledge Base]

Q --> Q2[Document]

Q --> Q3[Chunk Text + Metadata]


J1 --> R[Chunk ID Mapping]

J2 --> R

R --> Q3
```

