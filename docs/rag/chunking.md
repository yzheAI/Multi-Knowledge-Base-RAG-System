# Chunking Pipeline

## 1. 模块概述

Chunking Pipeline 负责将用户上传的原始文档转换为适合向量检索的文本块Chunk
在RAG系统中，Embedding模型和检索模块并不会直接处理完整的文档，而是首先将文档切分为Chunk后进行处理
因此Chunking的目标是：
- 保留文本的完整性
- 将Chunk长度控制在合适状态
- 为后续Embedding、FAISS检索、BM25检索提供所需要的数据
- 减少无意义文本进入向量库

整体流程；

```text
   Document
      ↓
Paragraph Split
      ↓
 Sentence Spilt
      ↓
 Sentence Merge
      ↓
 Chunk Cleaning
      ↓
  Final Chunks
```

## 2. Paragraph Split

### 2.1 功能
首先根据空行切分文档中的自然段
```text
paragraphs = re.split(
    r"\n\s*\n",
    text
)
```
根据 换行+任意空白字符+换行 来区分不同段落。

例：
输入：
```text
人工智能是一门研究智能机器的科学。

机器学习是人工智能的重要方向。
```

切分结果：
```text
[
 "人工智能是一门研究智能机器的科学。",
 "机器学习是人工智能的重要方向。"
]
```

### 2.2 切分Paragraph原因

如果按照固定长度切分，可能会破坏文档原有的语义边界。
可能会出现一个Chunk包含了两个自然段的内容，Embedding语义下降。
因此为了保证Chunk的完整性和语义分界，先按照自然结构划分。


## 3. Sentence Split

### 3.1 功能
Paragraph内部进一步按照句号、问号、感叹号等进行切分。
```text
sentences = re.split(
    r"(?<=[。！；？. ?])",
    paragraph
)
```
其中(?<=)表示匹配切分但是保留标点。

## 4. Sentence Merge

### 4.1 为什么不能每句作为一个Chunk
如果将每句话都作为一个Chunk，往往会造成语义信息不足。
Embedding模型通常需要一定上下文才能表达完整语义，
因此需要将多个相关句子合并成一个Chunk。

### 4.2 Chunk Size控制

```text
chunk_size=200
```

将一个Chunk控制在200个字符左右，当超过chunk_size限制时，
则对将文本拆分为多个Chunk，在尽量保证语义完整度的同时，
也没有因为Chunk过于庞大而降低语义密度。

## 5. Overlap 设计

```text
overlap_sentence = 1
```
作用：
相邻Chunk保留部分重复内容

原因：
- 防止文本上下文丢失
- 提高召回率

例如：
如果没有Overlap：
```text
Chunk1:
人工智能包括机器学习。

Chunk2:
深度学习是机器学习的重要方向。
```
当用户查询：
```text
Query: 深度学习属于人工智能哪个方向？
```
会出现：
- Chunk1 不包含深度学习。 
- Chunk2 不包含完整上下文。 
- Overlap 可以提高召回率。

## 6. Chunk Cleaning

生成Chunk后，为了提高检索的有效性，需要过滤无效内容。
```text
if not c:
    continue
```
过滤空文本。

### 6.1 过滤过段Chunk
```text
if len(c)<10:
    continue
```
例如各种标题，如目录、第一章、首页。
这些内容无检索价值，无需进入Chunk存储。

### 6.2 过滤纯标点文本
```text
if len(c.replace("。","").strip())==0:
    continue
```
避免垃圾数据进入向量库

## 7. 完整Pipeline

```text
            Document
               ↓
        split_paragraph()
               ↓
           Paragraph
               ↓
        split_sentence()
               ↓
        sentences_merge()
               ↓
         clean_chunks()
               ↓
         Final Chunks
               ↓
     Embedding + Vector Store
```

## 8. 当前实现优点

### 8.1 保留语义完整性
相比于固定长度切割，当前方法：
```text
Paragraph
+
Sentence
+
Overlap
```
更加符合自然语言结构，同时对Chunk长度进行了控制。

### 8.2 适合中文知识库
中文文档没有天然空格分词，因此使用句子级切分比token切割更加稳定


## 9. 当前不足与优化方向

### 9.1 未考虑文章结构
```text
# 标题

## 小节

正文
```
当前splitter会丢失标题信息

优化方向：
加入Markdown Header Splitter，保留标题+内容

### 9.2 基于字符长度切分

当前Chunk长度通过：
```text
len(text)
```
计算字符数量。
这种方式简单高效，但字符数量与LLM实际Token数量并不完全一致。

优化方向：
使用Tokenizer统计Token数量，使Chunk长度更加符合大模型上下文窗口限制。