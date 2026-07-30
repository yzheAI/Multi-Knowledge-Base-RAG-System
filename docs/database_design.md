# Database Design

## 1. Overview

在最初的版本，kb,documents,chunks等数据存储在本地文件，
但是后续引入了多知识库等功能，需要管理：
- 知识库信息
- 文档信息
- chunk数据(包括Metadata)
- chunk和向量索引的映射关系

所以引入MySQL对数据进行管理，存储结构化数据
同时保留Faiss和BM25检测索引，进行向量相似度匹配和关键词匹配

### 整体架构

MySQL
    |
    |
业务数据
    |
    +-- KnowledgeBase
    |
    +-- Document
    |
    +-- Chunk


FAISS
    |
chunk_id -> embedding


BM25
    |
chunk_id -> text


## 2. Database Tables

### KnowledgeBase
保存知识库信息

表名：knowledge_base

| 字段          | 类型       | 说明    |
|-------------|----------|-------|
| id          | int      | 主键    |
| name        | string   | 知识库名称 |
| description | string   | 描述    |
| created_at  | datetime | 创建时间  |


### Document
保存上传文本信息

表名：document

| 字段         | 类型       | 说明    |
|------------|----------|-------|
| id         | int      | 主键    |
| kb_id      | int      | 所属知识库 |
| filename   | string   | 文件名   |
| file_path  | string   | 文件路径  |
| created_at | datetime | 上传时间  |


### Chunk
保存文档切分后的chunks

表名：chunk

| 字段            | 类型   | 说明      |
|---------------|------|---------|
| id            | int  | 主键      |
| document_id   | int  | 所属文档    |
| content       | text | chunk文本 |
| chunk_index   | int  | chunk序号 |
| metadata_info | json | 元数据     |

作用：
- FAISS通过chunk_id找到embedding
- BM25通过chunk_id找到文本
- RAG生成阶段通过chunk_id查询原文


## 3. Table Relationship
```mermaid
erDiagram

    KNOWLEDGE_BASE ||--o{ DOCUMENT : contains
    DOCUMENT ||--o{ CHUNK : contains

    KNOWLEDGE_BASE {
        int id
        string name
    }

    DOCUMENT {
        int id
        int kb_id
        string filename
    }

    CHUNK {
        int id
        int document_id
        text content
    }