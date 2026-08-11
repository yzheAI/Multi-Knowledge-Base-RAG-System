from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import task_crud
from app.database.session import get_db

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.get("/{task_id}")
def get_task_status(
        task_id: str,
        db: Session = Depends(get_db)
):
    task = task_crud.get_task(
        db,
        task_id
    )

    return {
        "task_id": task.id,
        "status": task.status,
        "error": task.error_message
    }
