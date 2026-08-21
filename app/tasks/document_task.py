from app.services import document_service
from app.tasks.celery_app import celery_app
from app.database.session import SessionLocal
from app.crud import task_crud


@celery_app.task(bind=True)
def process_document_task(
        self,
        task_id,
        file_path,
        kb_path,
        filename,
        kb_name,
        owner_id
):
    db = SessionLocal()

    try:
        document_service.handle_document_upload(
            db,
            task_id,
            file_path,
            kb_path,
            filename,
            kb_name,
            owner_id
        )

    except Exception as e:

        task = task_crud.get_task(
            db,
            task_id,
            owner_id
        )

        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()

        raise

    finally:
        db.close()


