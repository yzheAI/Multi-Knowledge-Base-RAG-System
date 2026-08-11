from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.crud import task_crud
from app.database.session import get_db
from app.exceptions.exceptions import NotFoundTask
from app.models import User

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


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
