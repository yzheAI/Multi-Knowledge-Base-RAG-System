from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.task_schema import TaskSchema
from app.auth.dependencies import get_current_user
from app.crud import task_crud
from app.database.session import get_db
from app.exceptions.exceptions import NotFoundTask
from app.models import User

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.post("/create")
def create_task(
        request: TaskSchema,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
):
    task = task_crud.create_task(
        db=db,
        filename=request.filename,
        owner_id=user.id,
        task_id=request.task_id,
    )
    return {
        "task_id": request.task_id,
        "filename": request.filename,
        "owner_id": user.id,
        "created_at": task.created_at,
        "status": task.status,
    }


@tasks_router.get("/tasks")
def get_all_tasks(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    tasks = task_crud.get_tasks(
        db,
        user.id,
    )
    return {
        "data": [
            {
                "task_id": task.task_id,
                "filename": task.filename,
                "status": task.status,
                "created_at": task.created_at,
                "error": task.error_message
            }
            for task in tasks
        ]
    }


@tasks_router.get("/{task_id}")
def get_task_status(
        task_id: str,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    task = task_crud.get_task(
        db,
        task_id,
        user.id
    )

    if not task:
        raise NotFoundTask()

    return {
        "task_id": task.task_id,
        "status": task.status,
        "filename": task.filename,
        "created_at": task.created_at,
        "error": task.error_message
    }


@tasks_router.delete("/{task_id}")
def delete_task(
        task_id: str,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    task = task_crud.delete_task(
        db,
        task_id,
        user.id
    )

    if not task:
        raise NotFoundTask()

    return {
        "task_id": task.task_id,
        "status": "task deleted",
    }

