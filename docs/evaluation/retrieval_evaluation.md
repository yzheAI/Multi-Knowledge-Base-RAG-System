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
            "text": "xxx"
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
- text：与问题相关的知识库Chunk及其原始文本证据
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

## 4. Retrieval Evaluation Method

在132条测试问题上，对Faiss、BM25和Hybrid Retrieval进行了对比。

### 4.1 Evaluation Metrics

采用以下指标评价检索结果：

- Recall@1：相关 Chunk 是否出现在 Top-1
- Recall@3：相关 Chunk 是否出现在 Top-3
- Recall@5：相关 Chunk 是否出现在 Top-5
- MRR：相关 Chunk 首次出现位置的倒数平均值

### 4.2 Text-based Relevance Judgment

由于 Chunk ID 会随着 Chunking 策略变化而发生变化，
因此不能简单依赖固定 chunk_id 判断检索是否成功。

当前评估采用基于文本证据的 relevance judgment。
对于检索结果与 Ground Truth 文本，首先进行文本标准化，然后计算字符级 n-gram 重叠程度。

当满足以下任一条件时，将检索结果视为相关：
result_coverage >= 0.70
OR
expected_coverage >= 0.70

其中：

result_coverage：检索结果文本中能够被 Ground Truth 覆盖的比例
expected_coverage：Ground Truth 中能够被检索结果覆盖的比例

## 5. Baseline Retrieval Results

在早期版本的 118 条测试问题上，
对 Faiss、BM25 和 Hybrid Retrieval 进行了初始实验。

### 5.1 Faiss
| Metric   | Value |
|----------|-------|
| Recall@1 | 0.245 |
| Recall@3 | 0.364 |
| Recall@5 | 0.415 |
| MRR      | 0.309 |

### 5.2 BM25
| Metric   | Value |
|----------|-------|
| Recall@1 | 0.475 |
| Recall@3 | 0.695 |
| Recall@5 | 0.720 |
| MRR      | 0.575 |

### 5.3 Hybrid Retrieval
| Metric   | Value |
|----------|-------|
| Recall@1 | 0.619 |
| Recall@3 | 0.737 |
| Recall@5 | 0.754 |
| MRR      | 0.678 |

早期实验表明：
- Hybrid Retrieval 的整体效果最好
- BM25 明显优于 Faiss
- Hybrid 在 Recall@1 和 MRR 上相比于 BM25 有进一步提升
- 说明语义检索与关键词检索有一定互补性

上述结果作为项目早期 Retrieval Baseline，
后续实验进一步扩大了测试集，并对 Chunking 策略进行了改进。

## 6. Hybrid Retrieval Experiments

早期实验在 Hybrid Retrieval 内部，对不同融合与排序策略进行了实验。

| 方案 | 方法                  | Recall@1 | Recall@3 | Recall@5 | MRR    |
|----|---------------------|----------|----------|----------|--------|
| A  | Merge               | 25.42%   | 37.29%   | 42.37%   | 31.75% |
| B  | RRF_FUSION          | 38.14%   | 65.25%   | 68.64%   | 51.43% |
| C  | Merge+Reranker      | 43.22%   | 49.15%   | 50.85%   | 46.43% |
| D  | RRF Fusion+Reranker | 61.96%   | 73.73%   | 75.42%   | 67.75% |

实验结果表明，RRF Fusion 与 Reranker 结合能够取得更好的检索效果。

## 7. Chunking Strategy Experiment

在确定 Hybrid Retrieval 基础方案后，
进一步研究 Chunking 策略对工业技术文档检索效果的影响。

### 7.1 V1: Baseline Chunking

V1 使用基础的文本切分策略：
- 基于文本/句子进行切分
- Chunk Size ≈ 200
- 保留一定的句子重叠

该版本作为后续 Chunking 实验的 Baseline。

### 7.2 V2: Structure-aware Chunking

V2 在基础 Chunking 的基础上引入文档结构信息：
- 自动识别章节标题
- 自动识别小节标题
- 在章节和小节边界处进行 Chunk 切分
- 避免在重要结构边界处直接切断文本
- 保留章节/小节信息作为 Chunk Metadata
- Chunk Size 仍保持约 200，避免仅通过扩大 Chunk Size 获得提升

因此，V2 的核心变化并不是简单扩大 Chunk，而是：
利用工业技术文档自身的章节结构改善 Chunk 边界。

## 8. V1 vs V2 Retrieval Results
在相同的 132 条测试问题上，对 V1 和 V2 两种 Chunking 策略分别进行评估。

### 8.1 Faiss
| Version     | Recall@1  | Recall@3  | Recall@5  | MRR    |
|-------------|-----------|-----------|-----------|--------|
| V1          | 30.30%    | 40.91%    | 52.27%    | 0.377  |
| V2          | 40.91%    | 59.09%    | 63.64%    | 0.498  |
| Improvement | +10.61 pp | +18.18 pp | +11.37 pp | +0.121 |

### 8.2 BM25
| Version     | Recall@1 | Recall@3  | Recall@5 | MRR    |
|-------------|----------|-----------|----------|--------|
| V1          | 63.64%   | 76.52%    | 81.06%   | 0.704  |
| V2          | 73.48%   | 87.88%    | 90.15%   | 0.804  |
| Improvement | +9.85 pp | +11.36 pp | +9.09 pp | +0.101 |

### 8.3 Hybrid Retrieval
| Version     | Recall@1  | Recall@3  | Recall@5 | MRR    |
|-------------|-----------|-----------|----------|--------|
| V1          | 70.45%    | 79.55%    | 83.33%   | 0.758  |
| V2          | 83.33%    | 90.91%    | 91.67%   | 0.869  |
| Improvement | +12.88 pp | +11.36 pp | +8.34 pp | +0.111 |

### 8.4 Analysis

实验结果表明，V2 在三种 Retriever 上均取得稳定提升。

其中 Hybrid Retrieval + V2 的效果最佳：
- Recall@1：83.33%
- Recall@3：90.91%
- Recall@5：91.67%
- MRR：0.869

相比于V1：
- Recall@1 提升 12.88 个百分点
- Recall@3 提升 11.36 个百分点
- Recall@5 提升 8.34 个百分点
- MRR 提升 0.111

这表明在当前工业技术文档数据集上，结合章节和小节结构进行 Chunk 划分，
相比基础文本切分能够获得更好的检索效果。

同时，Recall@3 已达到 90.91%，而 Recall@5 为 91.67%，二者差距仅为 0.76 个百分点，
说明大多数成功召回的相关信息已经能够进入 Top-3。

因此，当前实验将 V2 Chunking + Hybrid Retrieval 作为主要检索方案。

## 9. V2 Answer Evaluation

在 Retrieval Evaluation 的基础上，进一步对RAG系统最终生成的答案进行质量评估。
采用 LLM 测评方法，使用 Qwen 对模型生成的答案进行评价。

评价指标：
- Correctness：答案与参考答案的一致程度
- Faithfulness：答案中的信息是否能够得到知识库上下文支持
- Relevance：答案是否直接回答用户问题

每项指标采用 1~5分评价

### 9.1 Answer Evaluation Results

在与 Retrieval Evaluation 相同的 132 条测试问题上进行 V2 Answer Evaluation。

| Metric       | Average |
|--------------|---------|
| Correctness  | 4.60/5  |
| Faithfulness | 4.82/5  |
| Relevance    | 4.79/5  |

### 9.2 Analysis

结果表明，V2 Chunking + Hybrid Retrieval 所产生的检索上下文能够较好地支持最终答案生成。

结果显示：
- Correctness = 4.60：模型答案整体与参考答案保持较高一致性。
- Faithfulness = 4.82：模型生成内容大部分能够从检索到的知识库上下文中获得支持。
- Relevance = 4.79：模型答案整体能够较好地围绕用户问题进行回答。

其中 Faithfulness 和 Relevance 均接近 5 分，说明当前 RAG 系统在知识库约束下的答案生成质量较高。

## 10. Current Retrieval Configuration

当前最终 Retrieval 配置如下：

| Component          | Configuration               |
|--------------------|-----------------------------|
| Dense Retrieval    | Faiss                       |
| Sparse Retrieval   | BM25                        |
| Fusion             | RRF                         |
| Faiss Top-K        | 10                          |
| BM25 Top-K         | 10                          |
| RRF Candidate Size | 10                          |
| Reranker           | bge-reranker-base           |
| Final Top-K        | 5                           |
| Chunking           | V2 Structure-aware Chunking |
| Evaluation Dataset | 132 QA                      |
| Answer Evaluation  | LLM-as-a-Judge              |

当前最佳 Retrieval 结果：

Hybrid + V2

- Recall@1 = 83.33%
- Recall@3 = 90.91%
- Recall@5 = 91.67%
- MRR      = 0.869

## 11. Conclusion

本实验围绕工业技术文档 RAG 系统，从检索和答案生成两个层面对系统进行了评估。

实验结果表明：
- Hybrid Retrieval 优于单独使用 Faiss 或 BM25，说明语义检索和关键词检索具有一定互补性。
- V2 Structure-aware Chunking 在 Faiss、BM25 和 Hybrid Retrieval 上均取得提升，说明利用技术文档章节结构优化 Chunk 边界能够改善检索效果。
- 当前最佳检索方案为 V2 Chunking + Hybrid Retrieval，其 Recall@1、Recall@3、Recall@5 分别达到 83.33%、90.91%、91.67%，MRR 达到 0.869。
- 在 132 条测试问题上的 Answer Evaluation 中，Correctness、Faithfulness 和 Relevance 分别达到 4.60、4.82 和 4.79 / 5。
