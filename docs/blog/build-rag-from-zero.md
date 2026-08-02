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


## 10. 后续优化