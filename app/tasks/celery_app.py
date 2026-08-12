from celery import Celery


celery_app = Celery(
    "rag",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=[
            "app.tasks.document_task",
        ]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
)
