# Task任务系统

## 1. Overview

Task模块用于处理知识库上传后的异步处理任务。
文档上传后，不直接在API请求中完成解析、切分、Embedding、向量存储等耗时操作，
而是创建Task并交给Celery异步执行。

整体流程：
```text
用户上传文件
    ↓
Upload Service
    ↓
Save Uploaded File
    ↓
 创建Task
    ↓
  Celery
    ↓
Document Processing
    ↓
 更新Task状态进度
```

## 2. Task状态

Task共有四种状态：
- PENDING
- PROCESSING
- SUCCESS
- FAILED

状态转换关系：
```text
PENDING
   ↓
PROCESSING
   |
   |————>SUCCESS
   |————>FAILED
           ↓
         手动Retry
           ↓
          PENDING
```

## 3. State Machine

为了避免不同模块直接修改Task状态，出现状态转换的逻辑不合理，
使用state_machine.py统一管理状态转换。

Task模块中允许的状态转换：
- PENDING → PROCESSING
- PROCESSING → SUCCESS
- PROCESSING → FAILED
- FAILED → PENDING

如果状态不合法，则会抛出 ValueError。
这样可能避免出现 SUCCESS → PROCESSING 等非法状态转换。

## 4. Task创建

用户上传文件后，在upload_service.py中创建Task，此时：
```text
status = PENDING
progress = 0
retry_count = 0
```
Task 同时保存：
```text
task_id
filename
owner_id
kb_id
file_path
kb_path
```
其中file_path和kb_path用于后续Celery任务执行以及失败后的手动Retry。

创建Task后，通过：
process_document_task.delay(...)
将任务提交给Celery。

## 5. Task执行

Celery获得任务后，调用`document_service.handle_document_upload(...)`进行实际的文档处理。
主要流程：
```text
PENDING 
   ↓ 
PROCESSING
   ↓ 
 解析文档
   ↓ 
生成chunks 
   ↓
保存Document
   ↓
 保存Chunk 
   ↓ 
 生成向量 
   ↓ 
 更新FAISS 
   ↓ 
 保存FAISS
   ↓ 
删除Retrieval Cache 
   ↓
 SUCCESS
```

## 6. Task进度

Task使用progress记录处理进度。
当前主要进度节点：
```text
10% 开始处理文档
30% 文档处理完成
50% Chunk保存完成
80% 向量索引更新完成
90% FAISS保存完成
100% 文档处理完成
```

进度主要用于前端展示任务执行情况。

## 7. Task失败处理
如果文档处理过程中出现异常，Celery Task会捕获异常。
```text
    except Exception as e:

        task = task_crud.get_task(
            db,
            task_id,
            owner_id
        )

        if task:
            transition_task(
                task,
                TaskStatus.FAILED,
            )
            task.error_message = str(e)
            db.commit()

        raise
```
此时：
```text
PROCESSING
    ↓
Exception
    ↓
 FAILED
```
同时将异常信息保存到error_message，方便前端查看任务失败原因。

## 8. 手动Retry

对于失败的Task，系统提供手动Retry接口，Retry只针对FAILED状态的Task，
经过retry_count限制判断后，若<3:
```text
retry_count += 1 
progress = 0 
error_message = None 
status = PENDING
```
然后重新提交Celery Task，Retry不会创建新的Task，而是获得原有Task信息，重新使用原有的task_id。

## 9. Retry次数限制

当前最大手动Retry次数为：MAX_RETRY_COUNT = 3。
当task.retry_count >= MAX_RETRY_COUNT时，不允许继续 Retry，
并抛出：RetryCountLimit。
因此一个Task最多可以进行3次手动Retry。

## 10. Retry条件

只有满足以下条件时才能 Retry：
- Task 存在
- Task 状态为 FAILED
- retry_count < MAX_RETRY_COUNT

## 11. 总结

当前Task系统主要负责：

```text
Task 创建
    ↓
Celery 异步执行
    ↓
状态管理
    ↓
进度管理
    ↓
异常处理
    ↓
失败后的手动 Retry
```

当前采用手动Retry，不使用Celery自动Retry。

对于：
- KnowledgeBaseEmptyError
- DocumentEmptyError
等确定性的业务错误，直接将Task标记为FAILED，由用户在问题解决后决定是否手动Retry。
这样可以避免对确定性错误进行无意义的重复执行。