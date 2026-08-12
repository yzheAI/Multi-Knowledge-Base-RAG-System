from app.models.task import Task


def create_task(db, task_id, filename, owner_id):

    task = Task(
        task_id=task_id,
        filename=filename,
        status="pending",
        owner_id=owner_id,
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


def update_task_status(db, task_id, status, owner_id):
    task = get_task(
        db,
        task_id,
        owner_id
    )

    if task:
        task.status = status
        db.commit()


def delete_task(db, task_id, owner_id):
    task = get_task(db, task_id, owner_id)

    if not task:
        return False

    db.delete(task)
    db.commit()

    return task


def get_tasks(db, owner_id):
    tasks = (
        db.query(Task)
        .filter(Task.owner_id == owner_id)
        .order_by(Task.created_at.desc())
        .all()
    )
    return tasks
