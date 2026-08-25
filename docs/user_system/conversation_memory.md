# Conversation Memory Design

## 1. 模块概述

AI知识库助手支持多轮对话功能，用户可以基于同一个对话进行连续提问。

为了支持：
- 多用户隔离
- 多会话管理
- 历史消息持久化
- 上下文连续性

系统设计了Conversation Memory模块。

该模块负责：
- 创建和管理Conversation
- 保存用户和LLM的交互记录
- 加载历史消息
- 为Prompt构建提供上下文

系统采用数据库持久化的方式进行保存对话，不依赖Python进程内存。

## 2. 为什么需要Conversation Memory

普通RAG流程：
```text
User Query
    ↓
 Retriever
    ↓
  Context
    ↓
   LLM
```
每次请求都是独立的，如果没有历史记录，在后续的提问中，若出现“它”等词汇，
LLM可能无法理解其具体含义。因此使用历史记录后：
```text
Query
+
Conversation History
+
Retrieved Context
↓
LLM
```

## 3. 设计方案演进

#### 初始方案：Memory对象

早期使用Python内存保存：
```text
Chat Service
    ↓
MemoryManager
    ↓
 Python List
```
存在问题：
- 服务重启后数据丢失
- 多用户难以隔离
- 无法进行历史查询

因此后续迁移到数据库持久化方案。

## 4. 当前架构

```text
User Query
      |
      ↓
Chat Service
      |
      +----------------+
      |                |
      ↓                ↓
Conversation       Retriever
History              |
      |              ↓
      +--------> Prompt Builder
                       |
                       ↓
                      LLM
                       |
                       ↓
                   Save Message
```

数据存储：
```text
 Conversation Table
        |
        ↓
 Message Table 
```

## 数据模型设计

### 5.1 Conversation

Conversation表示一次完整对话。
字段：

| 字段              | 说明     |
|-----------------|--------|
| id              | 数据库主键  |
| conversation_id | 业务会话ID |
| user_id         | 用户ID   |
| kb_id           | 所属知识库  |
| title           | 会话标题   |
| create_at       | 创建时间   |

作用：
- 区分不同用户
- 区分不同知识库
- 管理多个聊天窗口

### 5.2 Message

Message表示单次消息。

字段：

| 字段              | 说明   |
|-----------------|------|
| id              | 消息ID |
| conversation_id | 所属会话 |
| role            | 角色   |
| content         | 消息内容 |
| created_at      | 创建时间 |

例如：
```text
Conversation
      |
      |
 +----+----+
 |         |
Message  Message

user     assistant

问题      回答
```

## 6. Chat流程
完整流程：
```text
用户输入问题
    ↓
API Layer
    ↓
Chat Service
    ↓
查询Conversation History
    ↓
Retriever
    ↓
Prompt构建
    ↓
LLM生成回答
    ↓
Streaming返回
    ↓
保存Message    
```

## 7， History加载
当前版本会加载当前Conversation全部历史消息。

由于长对话可能导致Token增长，
未来可以优化为：

- 最近N轮历史
- Sliding Window
- History Summary

## 8. Conversation History与RAG结合

Prompt结构：
```text
Conversation History
      +
Retrieved Context
      +
 Current Question
```

## 9. Conversation Memory与Retriever关系

Conversation Memory负责保存：
- 用户之前说了什么
- LLM之前回答了什么

Retriever负责：
- 从知识库获取相关文档

二者结合：
Conversation History:
- 解决指代问题
Retrieved Context:
- 提供专业知识

构造Prompt交给LLM。

## 10. 数据隔离

系统通过user_id进行用户隔离。

conversation_id作为会话唯一标识。

kb_id用于关联当前Conversation所属知识库，
保证检索阶段使用正确知识库。