# Retriever Pipeline

## 1. 整体设计

检索模块根据用户输入的问题，
从指定的知识库中召回最匹配的chunks

系统采用了 Hybrid Retrieval 架构
包括：
- Faiss向量检索
- BM25关键词检索
- CrossEncoder重排序

实现结合语义匹配和关键词匹配两种方式来提高召回的效果

## 流程

Query

↓

向量 + 关键词

↓

Faiss Sematic Retrieval
BM25 Keyword Retrieval

↓

Merge合并

↓

Deduplication

↓

CrossEncoder Rerank

↓

Top-k Context

↓

LLM Generation



# 2. FaissRetriever


## 入口
`app/retriever/faiss_retriever.py`


## 功能

- 通过向量相似度进行语义检索


## 流程

User Query

↓

Query Embedding

↓

Faiss Index Search

↓

返回最相似的 chunk_id + score

↓

MySQL 通过chunk_ids查找chunks

↓

根据metadata进行filter筛选

↓

返回统一结果格式



# 3. BM25Retriever


## 入口
`app/retriever/bm25_retriever.py`


## 功能

- 根据关键词匹配进行检索


## 流程

User Query

↓

Jieba 分词

↓

关键词相关性get_score

↓

返回最匹配的 chunk_id + score

↓

MySQL 通过chunk_ids查找chunks

↓

根据metadata进行filter筛选

↓

返回统一结果格式



# 4. CrossEncoder Rerank


## 入口
`app/retriever/rerank.py`


## 功能：

- 对Faiss和BM25召回的chunks第二次排序
- 输入(query, chunk_text)
- 输出(rerank_score)



# 5. Unified Retrieval Result

由于FAISS和BM25返回结构不同
同时可以进行代码复用
所以通过build_retriever_results统一格式

统一格式：
{
    "text": chunk.content,
    "chunk_id": chunk.id,
    "score": score,
    "source": "faiss/bm25",
    "metadata": metadata
}

直接合并不同来源结果