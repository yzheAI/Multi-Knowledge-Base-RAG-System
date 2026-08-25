# Prompt 设计


## 1. 模块概述

Prompt负责组织输入信息，以此约束LLM回答范围，降低模型幻觉。

## 2. RAG Prompt结构

```text
Knowledge Context
+
Conversation History
+
User Question
```

## 3. System Prompt设计

例如：

```text
你是企业知识库助手，
只能根据提供资料回答。
如果资料不足，请回答：未在知识库中找到相关信息。
```

## 4. Context构建

Retrieved chunks:

chunk1
chunk2
chunk3

拼接：

Context:
{documents}

Question:
{query}


## 5. 防止幻觉

限制：

- 不允许编造
- 不确定时说明
- 优先引用知识库内容
