# LLM 设计

## 1. 模块概述

LLM Service负责封装大模型通用逻辑，
为上层Chat Service提供统一接口。

## 2. 为什么需要LLM Service

如果Chat Service直接调用模型：
```text
Chat Service
    |
    ↓
OpenAI API
```
会导致：
- 业务逻辑和模型耦合
- 难以替换模型
- 难以统一管理参数

因此设立LLM Service层：
```text
Chat Service
    |
    ↓
LLM Service
    |
    ↓
  具体模型
```

## 3. 核心职责

LLM Service主要负责：
- 模型调用封装
- Prompt传递
- 参数管理
- Streaming响应处理

## 4. Streaming设计
普通：
```text
请求
 ↓
等待完整回答
 ↓
返回
```

streaming：
```text
请求
 ↓
LLM生成token
 ↓
SSE实时返回
```

## 5. 模型替换
统一接口：

LLM Service

支持：

- OpenAI
- Qwen
- ChatGLM

## 6. 异常处理

LLM调用可能出现：

- API超时
- 模型服务不可用

因此LLM Service统一捕获异常，
向上层返回统一错误信息。
