from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.tasks.celery_app import celery_app
from app.document.pipeline import process_document
from app.database.session import SessionLocal
from app.crud import task_crud, document_crud, chunk_crud, knowledge_base
from app.core.container import container
from datetime import datetime
from app.knowledge_base.manager import KnowledgeManager
from app.config import KNOWLEDGE_BASE_PATH


@celery_app.task(bind=True)
def process_document_task(
        self,
        task_id,
        file_path,
        filename,
        kb_name,
        owner_id
):
    db = SessionLocal()

    try:
        task_crud.update_task_status(
            db,
            task_id,
            "processing",
            owner_id
        )

        kb = knowledge_base.get_kb_by_name(
            db,
            kb_name,
            owner_id
        )

        if not kb:
            raise KnowledgeBaseEmptyError()

        # 获取chunk信息
        result = process_document(
            file_path,
        )

        # 上传doc至MySQL
        doc = document_crud.create_document(
            db=db,
            kb_id=kb.id,
            filename=filename,
            file_path=file_path,
        )

        # 构建metadata，存入chunks，上传至SQL
        metadata = result["metadata"]

        metadata.update({
            "source": filename,
            "upload_time": datetime.now().isoformat()
        })

        chunks = chunk_crud.create_chunks(
            db=db,
            document_id=doc.id,
            chunks=result["chunks"],
            metadata=metadata
        )
        # 使用数据库生成的chunk_id建立向量索引
        chunk_ids = [
            chunk.id
            for chunk in chunks
        ]

        store = container.vector_manager.get_store(
            kb_name,
            db,
            owner_id
        )
        store.add(
            result["vectors"],
            result["chunks"],
            chunk_ids=chunk_ids,
        )
        # 获取知识库路径
        kdg = KnowledgeManager(
            KNOWLEDGE_BASE_PATH
        )

        kb_path = kdg.get_path(
            kb_name,
            owner_id
        )

        store.save(kb_path)

        container.vector_manager.remove_store(kb_name)

        task_crud.update_task_status(
            db,
            task_id,
            "success",
            owner_id
        )

        return True

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


