from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.task_schema import TaskResponse, TaskListResponse
from app.auth.dependencies import get_current_user
from app.crud import task_crud
from app.database.session import get_db
from app.exceptions.exceptions import NotFoundTask
from app.models import User
from app.services.task_service import retry_task_service

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.get(
    "/tasks",
    response_model=TaskListResponse,
)
def get_all_tasks(
        kb_id: int,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    tasks = task_crud.get_tasks(
        db,
        user.id,
        kb_id
    )
    return {
        "data": [
            {
                "task_id": task.task_id,
                "filename": task.filename,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
                "error": task.error_message
            }
            for task in tasks
        ]
    }


@tasks_router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
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
        "progress": task.progress,
        "created_at": task.created_at,
        "error_message": task.error_message
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


@tasks_router.post("/{task_id}/retry")
def retry_task(
        task_id: str,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    task = retry_task_service(
        db,
        task_id,
        user.id
    )

    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "retry_count": task.retry_count,
    }

