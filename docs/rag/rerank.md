# Reranker Pipeline

## 1. 模块概述

Reranker Pipeline负责对Hybrid Retrieval + RRF召回的候选Chunk进一步进行相关性判断。

系统首先通过FAISS和BM25进行高效召回，再通过RRF融合两个检索器的排名，
得到候选Chunk，由于RRF主要根据候选文档在不同检索器中的排名进行融合，
不能判断Query和Chunk的语义匹配程度，因此使用CrossEncoder Reranker
对候选结果进行精排。

```text
User Query
    |
    v
FAISS + BM25
    |
    v
   RRF
    |
    v
Candidate Chunks
    |
    v
Query + Chunk
    |
    v
Tokenizer
    |
    v
CrossEncoder Reranker
    |
    v
Relevance Score
    |
    v
   Sort
    |
    v
Top-K Chunks
```

## 2. Embedding Model 与 Reranker Model

系统中的Embedding Model和Reranker Model不是同一个模型，具有不同的职责。

### Embedding Model
Embedding Model使用BiEncoder思路，将Query或Chunk独立转换为向量：
```text
Query → Embedding Model → Query Vector
Chunk → Embedding Model → Chunk Vector
```
在Embedding之后，通过FAISS计算向量相似度，实现高效语义召回。

### Reranker Model
Reranker 使用CrossEncoder，将Query和Chunk一起输入模型：
```text
(Query, Chunk)
       |
       v
CrossEncoder
       |
       v
Relevance Score
```
CrossEncoder可以让Query和Chunk中的Token进行充分交互，对候选结果可以进行更精细的相关性判断。
但是CrossEncoder推理成本很高，因此不可以直接处理整个知识库，而是只处理FAISS+BM25+RRF召回的少量候选Chunk。

## 3. 模型加载
```text
tokenizer = AutoTokenizer.from_pretrained(
    RERANK_MODEL_PATH,
    use_fast=False
)
rerank_model = AutoModelForSequenceClassification.from_pretrained(
    RERANK_MODEL_PATH
)
```
此处tokenizer和rerank_model来自同一个RERANK_MODEL_PATH，但职责不同。

### Tokenizer
Tokenizer负责将文本转换成模型能够处理的Tensor
```text
Query + Chunk
      |
      v
Tokenizer
      |
      +-- input_ids
      +-- attention_mask
```

### Rerank Model
AutoModelForSequenceClassification加载真正的Transformer Reranker模型，
用于根据Query和Chunk预测相关性分数。
```text
Tokenizer
    +
Reranker Model
    =
完整的 Reranker 推理流程
```
tokenizer和rerank_model都从同一个RERANK_MODEL_PATH加载，但它们不是两个模型，
而是同一个Reranker的两个组成部分。Tokenizer负责将文本转换为模型输入，Reranker Model负责根据输入计算相关性分数。

## 4. 懒加载与全局缓存
```text
rerank_model = None
tokenizer = None

rerank_lock = threading.Lock()
```
Reranker模型较大，因此使用懒加载方式。
在程序启动时：
```text
rerank_model = None
```
当第一次执行Reranker时才真正加载模型。
```text
def get_rerank_model():
    global rerank_model, tokenizer

    if rerank_model is None:
        with rerank_lock:
            if rerank_model is None:
                ...
```
模型加载后保存在全局变量中，后续请求可以直接复用，不需要重复加载。
threading.Lock()用来防止并发请求重复加载模型。
第一次检查避免已经加载完成的情况下频繁获取锁；第二次检查用于防止等待锁的过程中模型已经被其他线程加载。

## 5. 推理模式

模型加载完成后，需要将模型移动到指定设备，并设置为推理模式，关闭训练阶段一些行为
```text
rerank_model.to(DEVICE)
rerank_model.eval()
```
在实际推理时，使用torch.no_grad()禁止梯度计算。
```text
with torch.no_grad():
    outputs = model(**inputs)
```
Reranker在精排时只负责推理，不需要反向传播和参数更新，因此可以减少内存占用和计算开销。

## 6. 构造Query-Chunk Pairs
```text
pairs = [
    (query, doc["text"])
    for doc in docs
]
```
每一个 (Query, Chunk) 都是一个需要进行相关性判断的文本对。

## 7. Tokenizer编码
```text
inputs = tokenizer(
    pairs,
    padding=True,
    truncation=True,
    return_tensors="pt"
)
```
其中：
- padding=True：将一个Batch中长度不同的文本补齐到相同长短
- truncation=True：当文本超过模型允许最大长度时进行截断
- return_tensors="pt"：将结果转换成Pytorch Tensor。

## 8. 将输入移动到指定设备
```text
inputs = {
    k: v.to(DEVICE)
    for k, v in inputs.items()
}
```
模型和输入必须位于同一个设备，
例如：
```text
Model
  ↓
 GPU
  
Input Tensor
    ↓
   GPU
```

## 9. CrossEncoder推理
```text
with torch.no_grad():
    outputs = model(**inputs)
```
inputs是一个字典：
{
    "input_ids":...
    "attention_mask":...
}
因此使用model(**inputs)，等价于:
```text
model(
    input_ids=inputs["input_ids"],
    attention_mask=inputs["attention_mask"]
)
```
模型处理每一个 Query-Chunk Pair，并输出对应的预测结果。

## 10. 获取相关性分数
```text
scores = outputs.logits.squeeze(-1)
```
outputs.logits 是模型最后输出的原始预测分数。
假设当前有5个候选Chunk，模型对5个Query-Chunk Pair分别输出一个分数，因此outputs.logits的形状可能为[5, 1]，
使用squeeze(-1)去掉最后一个大小为1的维度，最后转换为一维数组，每个分数对应一个Query-Chunk Pair

## 11. 将分数写入Chunk并进行排序
```text
for doc, score in zip(docs, scores):
    doc["rerank_score"] = float(score)
```
每个Chunk都保存了CrossEncoder计算得到的相关性分数，后根据相关性分数进行排序。
```text
docs = sorted(
    docs,
    key=lambda x: x["rerank_score"],
    reverse=True
)
```
按照rerank_score从高到低进行排序，例如：
```text
Doc1 → 5
Doc2 → 3
Doc3 → 6
Doc4 → 7
```
排序后：
```text
Doc4 → 7
Doc3 → 6
Doc1 → 5
Doc2 → 3
```
最后返回return docs[:top_k],top_k默认为5，
最终只保留相关性最高的 5 个 Chunk，交给后续 LLM 生成答案。

## 14. 为什么需要Reranker？

FAISS语义相似度检索，主要依靠向量空间中的相似度，BM25主要依赖关键词匹配，
而RRF虽然可以融合FAISS和BM25两种检索方式，但是RRF本身没有重新理解Query和Chunk语义关系的能力。
而Reranker可以进一步进行：
```text
Query + Chunk
      ↓
 CrossEncoder
      ↓
   相关性判断
```
因此最终形成了：
```text
召回阶段：
FAISS + BM25
      ↓
融合阶段：
     RRF
      ↓
精排阶段：
CrossEncoder
      ↓
生成阶段：
     LLM
```

## 15. 为什么不用CrossEncoder检索整个知识库
CrossEncoder计算成本很高，如果将Query与每个Chunk都进行CrossEncoder，
则需要进行大量的Query-Chunk配对计算，会极大地增加计算成本，
因此首先进行FAISS+BM25高效召回和RRF融合，缩小Chunk范围，
这样即保证了检索效率，又利用CrossEncoder提高了最终排序质量。
