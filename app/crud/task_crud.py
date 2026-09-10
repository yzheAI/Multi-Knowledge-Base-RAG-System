from app.models.task import Task
from app.tasks.state_machine import transition_task
from app.tasks.status import TaskStatus


def create_task(
        db,
        task_id,
        filename,
        owner_id,
        kb_id,
        file_path,
        kb_path,
        document_type
):

    task = Task(
        task_id=task_id,
        filename=filename,
        status=TaskStatus.PENDING,
        owner_id=owner_id,
        kb_id=kb_id,
        file_path=file_path,
        kb_path=kb_path,
        document_type=document_type
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_task(db, task_id, owner_id):
    task = (
        db.query(Task).
        filter(
            Task.task_id == task_id,
            Task.owner_id == owner_id,
        )
        .first()
    )
    return task


def delete_task(db, task_id, owner_id):
    task = get_task(db, task_id, owner_id)

    if not task:
        return False

    db.delete(task)
    db.commit()

    return task


def get_tasks(db, owner_id, kb_id):
    tasks = (
        db.query(Task)
        .filter(
            Task.owner_id == owner_id,
            Task.kb_id == kb_id,
        )
        .order_by(Task.created_at.desc())
        .all()
    )
    return tasks


def update_task_progress(
        db,
        task_id,
        progress,
        owner_id
):
    task = get_task(
        db,
        task_id,
        owner_id
    )

    if task is None:
        return None

    task.progress = max(
        0,
        min(progress, 100)
    )

    db.commit()
    db.refresh(task)
    return task


def retry_task(db, task_id, owner_id):
    task = get_task(
        db,
        task_id,
        owner_id
    )
    if task is None:
        return None

    task.retry_count += 1
    task.progress = 0
    task.error_message = None
    transition_task(
        task,
        TaskStatus.PENDING
    )

    db.commit()
    db.refresh(task)
    return task
