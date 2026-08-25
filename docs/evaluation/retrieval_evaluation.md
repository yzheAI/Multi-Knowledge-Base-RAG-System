# Retrieval Evaluation

## 1. Experiment Overview

为了评估不同检索策略在知识库问答系统中的效果，项目设计了检索评估模块，
对 Faiss、BM25、Hybrid Retrieval 三种方案进行对比

评价指标：
- Recall@K
表示匹配正确的 chunk 是否出现在前 K 个检索结果中。
- MRR
衡量正确 chunk 在检索列表中的排序质量。


## 2. Evaluation Dataset

测试数据来自系统已有知识库。

数据格式：
```json
  {
    "question": "...",
    "answer": "...",
    "source": "...",
    "kb_name": "...",
    "chunk_id": "..."
  }
```

其中：
- question：用户查询问题
- kb_name：所属知识库名字
- chunk_id：答案对应的chunk

## 3. Retrieval Strategies

### 3.1 Faiss Semantic Retrieval
流程：

    Query
      |
    Embedding
      |
    Vector Search
      |
    Top-K chunk

特点；
- 通过Faiss进行语义相似度对比
- 对自然语言表达变化适应性强
缺点：
- 对精准关键词匹配能力弱

### 3.2 BM25 Keyword Retrieval
流程：

    Query
      |
    Tokenization
      |
    BM25 Score
      |
    Top-k chunks

特点：
- 对专业名称、实体关键词效果好
缺点；
- 无法理解语义

### 3.3 Hybrid Retrieval
流程：

    Faiss + BM25
          |
     RRF Fusion
          |   
       Reranker
          |
        Result

其中：
将候选集进行扩大：candidate_k = 10
以此获取 Faiss Top20 + BM25 Top20
最后对候选集进行融合筛选

RRF Fusion
使用 Reciprocal Rank Fusion
不依赖不同检索器的score尺度，综合多个排序结果

Reranking
融合后的候选结果输入bge-reranker-base进行重新排序

## 4. Experiment Results
Faiss:

| Metric   | Value |
|----------|-------|
| Recall@1 | 0.259 |
| Recall@3 | 0.431 |
| Recall@5 | 0.500 |
| MRR      | 0.353 |


BM25:

| Metric   | Value |
|----------|-------|
| Recall@1 | 0.483 |
| Recall@3 | 0.741 |
| Recall@5 | 0.828 |
| MRR      | 0.609 |


## 5. Hybrid Retrieval Experiments

| 方案 | 方法                  | Recall@1 | Recall@3 | Recall@5 | MRR    |
|----|---------------------|----------|----------|----------|--------|
| A  | Merge               | 25.86%   | 43.10    | 50.00%   | 35.26% |
| B  | RRF_FUSION          | 31.03%   | 58.62%   | 74.14%   | 46.32% |
| C  | Merge+Reranker      | 44.83%   | 55.17%   | 55.17%   | 49.71% |
| D  | RRF Fusion+Reranker | 63.79%   | 86.21%   | 87.93%   | 74.28% |


## 6. Analysis
Reranker只能对输入候选集进行排序，如果没有正确的Chunk进入候选集，
即使Reranker很强也无法恢复。
因此可以扩大candidate_k提高召回效果

由于简单Merge存在以下问题：
- 不同Retriever排序空间不同
- 导致某一种召回结果完全占据前排
RRF通过rank进行融合
- 保留多个检索器优势
- 降低单一Retriever偏差

## 最终配置

| 组件               | 配置                |
|------------------|-------------------|
| Dense Retrieval  | Faiss             |
| Sparse Retrieval | BM25              |
| Fusion           | RRF               |
| Candidate Size   | 10                |
| Reranker         | bge-reranker-base |
| Final TopK       | 5                 |
