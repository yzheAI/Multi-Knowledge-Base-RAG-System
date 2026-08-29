from datetime import datetime
from pydantic import BaseModel
from app.tasks.status import TaskStatus


class TaskResponse(BaseModel):
    task_id: str
    filename: str
    status: TaskStatus
    progress: int
    created_at: datetime
    error_message: str | None = None


class TaskListResponse(BaseModel):
    data: list[TaskResponse]
