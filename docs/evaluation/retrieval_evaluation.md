# RAG Evaluation

## 1. Experiment Overview

为了评估不同检索策略在知识库问答系统中的效果，
以及工业知识库问答系统的整体效果，项目设计了检索评估模块，
分别从检索质量和答案质量两个维度进行评估。

评测分为两个部分：
- Retrieval Evaluation：评估不同检索策略对相关知识的召回能力
- Answer Evaluation：评估模型最终生成答案的正确性、知识库忠实性和问题相关性

整体流程：
```text
        RAG Evaluation
              |
    +---------+---------+
    |                   |
Retrieval Evaluation Answer Evaluation
    |                   |
Recall@K / MRR      Correction
                   Faithfulness
                    Relevance
```

## 2. Evaluation Dataset

测试数据来自系统已有知识库。

数据格式：
```json
  {
      "question": "...",
      "answer": "...",
      "kb_name": "...",
      "relevant_chunks": [
        {
            "source": "...", 
            "chunk_id": 123
        }
      ],
      "category": "..."
  }
```

其中：
- question：用户查询问题
- answer：参考答案
- kb_name：所属知识库名字
- relevant_chunks：与问题相关的知识库Chunk
- chunk_id：答案对应的chunk
- category：问题类型，包括fact、list、unanswerable、comparison、procedure

## 3. Retrieval Strategies

### 3.1 Faiss Semantic Retrieval
流程：
```text
    Query
      |
   Embedding
      |
  Vector Search
      |
   Top-K chunk
```

特点；
- 通过Faiss进行语义相似度对比
- 对自然语言表达变化适应性强
缺点：
- 对精准关键词、参数编号、报警号等工业领域信息的匹配能力较弱

### 3.2 BM25 Keyword Retrieval
流程：
```text
    Query
      |
  Tokenization
      |
   BM25 Score
      |
  Top-k chunks
```

特点：
- 对专业名称、实体关键词、参数编号等信息具有较好的匹配能力
缺点；
- 对语义相似但字面不同的表达理解能力有限

### 3.3 Hybrid Retrieval

流程：
```text
    Faiss + BM25
          |
     RRF Fusion
          |
   Candidate Top-K
          |   
       Reranker
          |
        Result
```

当前Hybrid Retrieval配置为：
- Faiss Top-K = 10
- BM25 Top-K = 10
- RRF Fusion后保留Top-10
- 使用 `bge-reranker-base` 进行重新排序
- 最终返回 Top-5

#### RRF Fusion
使用 Reciprocal Rank Fusion 对 Faiss 和 BM25 的检索结果进行融合。
不依赖不同检索器的score尺度，综合多个排序结果，从而降低不同检索器Score分布差异带来的影响。

#### Reranking
将 RRF 融合后的候选结果输入 bge-reranker-base 进行重新排序，
根据 Query 与候选 Chunk 的相关性重新排序，最终返回 Top-5 结果。

## 4. Experiment Results

在118条测试问题上，对Faiss、BM25和Hybrid Retrieval进行了对比。

### 4.1 Faiss

| Metric   | Value |
|----------|-------|
| Recall@1 | 0.254 |
| Recall@3 | 0.373 |
| Recall@5 | 0.424 |
| MRR      | 0.318 |


### 4.2 BM25:

| Metric   | Value |
|----------|-------|
| Recall@1 | 0.475 |
| Recall@3 | 0.695 |
| Recall@5 | 0.720 |
| MRR      | 0.575 |

### 4.3 Hybrid Retrieval

| Metric   | Value |
|----------|-------|
| Recall@1 | 0.627 |
| Recall@3 | 0.737 |
| Recall@5 | 0.754 |
| MRR      | 0.683 |

从结果来看：
- Hybrid Retrieval 的整体效果最好
- BM25 明显优于 Faiss
- Hybrid 在 Recall@1 和 MRR 上相比于 BM25 有进一步提升
- 说明语义检索与关键词检索有一定互补性

## 5. Hybrid Retrieval Experiments

| 方案 | 方法                  | Recall@1 | Recall@3 | Recall@5 | MRR    |
|----|---------------------|----------|----------|----------|--------|
| A  | Merge               | 25.42%   | 37.29%   | 42.37%   | 31.75% |
| B  | RRF_FUSION          | 38.14%   | 65.25%   | 68.64%   | 51.43% |
| C  | Merge+Reranker      | 43.22%   | 49.15%   | 50.85%   | 46.43% |
| D  | RRF Fusion+Reranker | 62.71%   | 73.73%   | 75.42%   | 68.32% |

实验结果表明，RRF Fusion 与 Reranker 结合能够取得更好的检索效果。

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


## 7. Answer Evaluation

在 Retrieval Evaluation 的基础上，进一步对RAG系统最终生成的答案进行质量评估。
采用 LLM 测评方法，使用 Qwen 对模型生成的答案进行评价。

评价指标：
- Correctness：答案与参考答案的一致程度
- Faithfulness：答案中的信息是否能够得到知识库上下文支持
- Relevance：答案是否直接回答用户问题

每项指标采用 1~5分评价

### 7.1 Answer Evaluation Results

共测评118条问题。

| Metric       | Average |
|--------------|---------|
| Correctness  | 4.01/5  |
| Faithfulness | 4.66/5  |
| Relevance    | 4.43/5  |

### 7.2 Analysis

结果显示：
- Faithfulness达到了4.66，说明模型生成答案整体能够较好地依据知识库内容
- Relevance达到了4.43，说明大多数答案能够围绕用户问题进行回答。
- Correctness为4.01，是三个指标中相对较弱的一项

Correctness较低的部分问题主要可能与检索未召回相关Chunk、答案信息遗漏、召回Chunk不完整等因素有关。

## 8. Final Configuration

| Component          | Configuration     |
|--------------------|-------------------|
| Dense Retrieval    | Faiss             |
| Sparse Retrieval   | BM25              |
| Fusion             | RRF               |
| Faiss Top-K        | 10                |
| BM25 Top-K         | 10                |
| RRF Candidate Size | 10                |
| Rerank             | bge-reranker-base |
| Final Top-K        | 5                 |
| Answer Model       | Qwen              |
| Answer Evaluation  | LLM-as-a-Judge    |
