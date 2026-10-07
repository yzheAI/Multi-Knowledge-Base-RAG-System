# Chunking Pipeline

## 1. 模块概述

Chunking Pipeline 负责将用户上传的原始文档转换为适合向量检索的文本块Chunk，
在RAG系统中，Embedding模型和检索模块并不会直接处理完整的文档，而是首先将文档切分为Chunk后进行处理，
因此Chunking的目标是：
- 保留文本的完整性
- 将Chunk长度控制在合适状态
- 为后续Embedding、FAISS检索、BM25检索提供所需要的数据
- 减少无意义文本进入向量库

当前项目采用两个版本的 Chunking 策略：

- V1：Baseline Chunking，主要基于 Paragraph + Sentence 进行切分
- V2：Structure-aware Chunking，在 V1 基础上进一步利用工业技术文档的章节和小节结构

整体流程：

v1:
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

v2:
```text
V2:

Document
   ↓
TOC / Page Number Filtering
   ↓
Structure Detection
   ├── Main Heading
   ├── Subheading
   └── Body Text
          ↓
    Sentence Split
          ↓
    Sentence Merge
          ↓
   Chunk + Section Metadata
          ↓
      Final Chunks
```

## 2. V1：Baseline Chunking

V1 是项目最初采用的基础 Chunking 策略，主要通过自然段、句子以及固定长度控制完成文本切分。

### 2.1 Paragraph Split

#### 2.1.1 功能

首先根据空行切分文档中的自然段
```text
paragraphs = re.split(
    r"\n\s*\n",
    text
)
```
根据换行+任意空白字符+换行来区分不同段落。

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

#### 2.1.2 切分Paragraph原因

如果按照固定长度切分，可能会破坏文档原有的语义边界。
可能会出现一个Chunk包含了两个自然段的内容，Embedding语义质量下降。
因此为了保证Chunk的完整性和语义分界，先按照自然段结构划分。


### 2.2. Sentence Split

#### 2.2.1 功能
Paragraph内部进一步按照句号、问号、感叹号等进行切分。
```text
sentences = re.split(
    r"(?<=[。！；？. ?])",
    paragraph
)
```
其中(?<=)表示匹配切分但是保留标点。

### 2.3. Sentence Merge

#### 2.3.1 为什么不能每句作为一个Chunk
如果将每句话都作为一个Chunk，往往会造成语义信息不足。
Embedding模型通常需要一定上下文才能表达完整语义，
因此需要将多个相关句子合并成一个Chunk。

#### 2.3.2 Chunk Size控制

```text
chunk_size=200
```

将一个Chunk控制在200个字符左右，当超过chunk_size限制时，
则对将文本拆分为多个Chunk，在尽量保证语义完整度的同时，
也没有因为Chunk过于庞大而降低语义密度。

### 2.4. Overlap 设计

```text
overlap_sentence = 1
```
#### 2.4.1 作用：
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

### 2.5 Chunk Cleaning

#### 2.5.1 过滤空文本

生成Chunk后，为了提高检索的有效性，需要过滤无效内容。
```text
if not c:
    continue
```
过滤空文本。

#### 2.5.2 过滤过段Chunk
```text
if len(c)<10:
    continue
```
例如各种标题，如目录、第一章、首页。
这些内容无检索价值，无需进入Chunk存储。

### 2.5.3 过滤纯标点文本
```text
if len(c.replace("。","").strip())==0:
    continue
```
避免垃圾数据进入向量库

## 3. V1 Pipeline

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

## 4. V1 的特点与局限

### 4.1 V1 的优点

#### 4.1.1 保留语义完整性
相比于固定长度切割，当前方法：
```text
Paragraph
+
Sentence
+
Overlap
```
更加符合自然语言结构，同时对Chunk长度进行了控制。

#### 4.1.2 适合中文知识库
中文文档没有天然空格分词，因此使用句子级切分比token切割更加稳定


### 4.2 V1的局限

V1 主要按照 Paragraph 和 Sentence 进行切分，但没有进一步利用工业技术文档自身的章节结构。

例如工业技术手册通常具有：
```text
第三章 参数设置
3.1 参数说明
正文……
3.2 参数配置
正文……
```

这些章节和小节本身包含重要的上下文信息。
V1 中：
Document
   ↓
Paragraph
   ↓
Sentence
   ↓
Chunk

并不会主动识别：
章节
小节
标题

因此可能出现：
Chunk 在章节边界附近被切断
同一章节的内容被分散到不同 Chunk
Chunk 缺少明确的章节上下文
对技术文档中的结构信息利用不足

因此，针对工业技术文档的特点，进一步设计了 V2 Structure-aware Chunking。

## 5. V2: Structure-aware Chunking

V2 在 V1 基础上引入文档结构信息。

其核心思想不是简单扩大 Chunk Size，而是：
- 利用工业技术文档自身的章节和小节结构优化 Chunk 边界。

主要改动包括：
- 自动识别章节标题
- 自动识别小节标题
- 在章节和小节边界处进行 Chunk 切分
- 保留章节和小节信息作为 Chunk Metadata
- Chunk Size 仍保持约 200
- 保留原有 Sentence Merge 和 Overlap 机制

因此 V2 的核心变化是：
V1:
```
文本内容
   ↓
Sentence-based Chunking
```

V2:
```
文档结构
   +
文本内容
   ↓
Structure-aware Chunking
```

## 6. V2 Structure Detection

V2 首先对原始文档进行结构识别。

根据 PDF 文档中的文本排版信息，对章节标题和小节标题进行识别。

主要利用：

- 字体大小
- 标题文本长度
- 中文章节格式
- 数字章节格式
- 文本所在页面结构

识别出的结构信息包括：

```
Chapter Heading
      ↓
  Subheading 
      ↓
  Body Text
```
V2 在检测到新的章节或小节时，会结束当前 Chunk 的生成，并以新的结构作为后续文本的上下文。

## 7. V1 vs V2

两种 Chunking 策略的主要区别：

| 项目              | V1         | V2             |
|-----------------|------------|----------------|
| Paragraph Split | √          | ×              |
| Sentence Split  | √          | √              |
| Sentence Merge  | √          | √              |
| Chunk Size      | ≈200       | ≈200           |
| Overlap         | 1 sentence | 1 sentence     |
| 章节结构识别          | ×          | √              |
| 小节结构识别          | ×          | √              |
| 结构信息            | 无          | Chunk Metadata |
| Chunk 边界        | 主要由文本长度决定  | 同时考虑文档结构       |
| 设计目标            | 通用文本切分     | 工业技术文档结构感知切分   |

因此：
V2 的核心并不是让 Chunk 变大，而是在保持 Chunk Size 基本不变的情况下，
利用工业技术文档的章节结构改善 Chunk 边界。

## 8. Chunking实验结果

为了验证 V2 Structure-aware Chunking 是否能够改善检索效果，
在相同的 132 条测试问题上，对 V1 和 V2 分别进行评估。

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
|

## 9. 实验分析

实验结果表明，V2 Structure-aware Chunking 在三种 Retriever 上均取得稳定提升。

其中：

V2 + Hybrid Retrieval

取得当前最佳结果：

- Recall@1：83.33%
- Recall@3：90.91%
- Recall@5：91.67%
- MRR：0.869

相比 V1：

- Recall@1 提升 12.88 个百分点
- Recall@3 提升 11.36 个百分点
- Recall@5 提升 8.34 个百分点
- MRR 提升 0.111

这说明在当前工业技术文档数据集上，在 Chunk Size 基本保持不变的情况下，
引入章节和小节结构能够改善 Chunk 边界，并进一步提升检索效果。

同时：

- Recall@3 = 90.91%
- Recall@5 = 91.67%

二者仅相差 0.76 个百分点。

这说明大多数能够成功召回的相关信息已经能够进入 Top-3，继续扩大候选范围带来的收益相对有限。

因此，当前项目将：

V2 Structure-aware Chunking
        +
Hybrid Retrieval

作为主要 RAG 检索方案。


## 10. 后续优化方向

当前 V2 已经通过 132 条测试问题完成了与 V1 的对比实验，并取得明显提升。

因此后续优化不再以简单调整 Chunk Size 为主要方向，而可以进一步关注：

### 10.1 结构信息利用

进一步研究章节、小节、页面等 Metadata 在：

- Retrieval
- Reranking
- Context Construction

中的作用。

### 10.2 Chunk与上下文关系

当前 Chunk Size 仍约为 200 字符，可以进一步研究不同文档类型下 Chunk 长度与检索效果之间的关系。

### 10.3 更复杂的文档结构

对于包含：

- 表格
- 图片
- 参数列表
- 多级标题

的工业技术文档，可以进一步研究针对不同文档元素的结构化 Chunking 方法。

## 11. 总结

当前项目的 Chunking 策略经历了：

```text
v1
Paragraph + Sentence + Length
            ↓
  发现工业技术文档存在结构信息
            ↓
v2
    Structure-aware Chunking
            ↓
         实验验证
            ↓
    V2 + Hybrid Retrieval      
```

实验结果表明：
```text
在当前工业技术文档数据集上，利用章节和小节结构优化 Chunk 边界，
相比基础的 Sentence-based Chunking 能够获得更好的检索效果。
```
