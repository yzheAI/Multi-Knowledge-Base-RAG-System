# Upload Pipeline:
## 入口：
`app/services/upload_service.py`


## 功能

负责完成用户上传文档后的完整数据处理流程，包括：

- 文件保存
- 文档解析
- Chunk切分
- Embedding生成
- MySQL数据持久化
- FAISS/BM25索引建立


## 流程：
Upload File

↓

process_document()

↓

{
chunks,
vectors,
metadata
}

↓

MySQL

↓

knowledge_base

↓

document

↓

chunk

↓

获取数据库生成的 chunk_id

↓

构建检索索引

↓

chunk_id + embedding

↓

FAISS Vector Index


chunk_id + text

↓

BM25 Keyword Index

## 设计核心
使用chunk_id作为检索索引唯一标识
先将chunks存入MySQL，自动生成chunk_id，
将chunk_id和embedding一一对应存入faiss
将chunk_id和关键词一一存入bm25

上传流程：
## 步骤：
1. 创建或者获取知识库
2. 将上传的文件存入目标知识库
3. 文档解析、chunk拆分、embedding生成
4. 创建doc和chunks，存入MySQL，并获取chunk_ids
5. 将chunk_ids和chunks提供给faiss，进行向量、索引存储







# delete
入口：app/services/upload_service.py


## 功能

删除知识库中的文档，并同步删除：

- MySQL中的document/chunk数据
- FAISS中的向量索引
- BM25中的关键词索引


## 流程
Delete Document Request

↓

根据document_id查询chunks

↓

获取chunk_ids

↓

删除FAISS索引

chunk_ids

↓

VectorStore.delete()


↓

重建BM25索引

保留:

remaining chunk_ids

↓

重新生成BM25 Store


↓

保存FAISS/BM25索引

↓

删除chunks

↓

删除documents

## 步骤：
1. 传入目标文档id以及kb路径
2. faiss_store删除目标chunks_ids
3. bm25_store选出需要保留的chunk_ids，重新存入
4. 进行重新faiss保存
5. 删除chunks
6. 删除文档

## 删除顺序设计

先删除检索索引，再删除数据库数据。

### 原因：
删除FAISS/BM25时需要依赖chunk_id, 如果提前删除MySQL chunk,
chunk_id对应关系丢失，无法准确同步索引
