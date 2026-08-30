from app.config import MAX_RETRY_COUNT
from app.crud import task_crud, knowledge_base
from app.exceptions.exceptions import NotFoundTask, TaskNotFailed, RetryCountLimit, KnowledgeBaseEmptyError
from app.tasks.status import TaskStatus
from app.tasks.document_task import process_document_task


def retry_task_service(db, task_id, owner_id):
    task = task_crud.get_task(
        db,
        task_id,
        owner_id=owner_id
    )

    if task is None:
        raise NotFoundTask()

    if task.status != TaskStatus.FAILED:
        raise TaskNotFailed()

    if task.retry_count >= MAX_RETRY_COUNT:
        raise RetryCountLimit()

    kb = knowledge_base.get_kb_by_id(
        db,
        kb_id=task.kb_id
    )

    if kb is None:
        raise KnowledgeBaseEmptyError("知识库不存在")

    task = task_crud.retry_task(
        db,
        task_id,
        owner_id
    )

    process_document_task.delay(
        task_id,
        task.file_path,
        task.kb_path,
        task.filename,
        kb.name,
        owner_id
    )

    return task
