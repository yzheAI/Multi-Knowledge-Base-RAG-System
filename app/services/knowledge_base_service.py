from app.config import KNOWLEDGE_BASE_PATH
from app.crud.knowledge_base import get_kb_by_name, get_all_kbs, delete_kb
from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.knowledge_base.manager import KnowledgeManager
from app.crud.document_crud import get_documents_by_kb
import os

from app.services.upload_service import file_delete


async def create(db, kb_name):

    kb = get_kb_by_name(db, kb_name)
    if kb:
        return {
            "id": kb.id,
            "name": kb.name,
            "created_at": kb.created_at,
        }

    kdg = KnowledgeManager(KNOWLEDGE_BASE_PATH)

    kb = kdg.create(db, kb_name)

    kb_path = kdg.get_path(kb_name)

    upload_dir = os.path.join(
        kb_path,
        "files"
    )

    os.makedirs(
        upload_dir,
        exist_ok=True
    )
    return {
        "id": kb.id,
        "name": kb.name,
        "created_at": kb.created_at,
    }


async def get_all_kb_service(db):
    kbs = get_all_kbs(db)
    result = [
        {
            "id": kb.id,
            "name": kb.name,
            "created_at": kb.created_at,
        }
        for kb in kbs
    ]
    return result


async def get_kb_service(db, kb_name):
    kb = get_kb_by_name(db, kb_name)
    if not kb:
        raise KnowledgeBaseEmptyError("无该知识库")

    docs = get_documents_by_kb(db, kb.id)

    return {
        "kb_id": kb.id,
        "kb_name": kb.name,
        "created_at": kb.created_at,
        "documents": [
            {
                "doc_id": doc.id,
                "doc_name": doc.filename,
                "created_at": doc.created_at,
            }
            for doc in docs
        ]
    }


async def delete_kb_service(db, kb_name):
    kb = get_kb_by_name(db, kb_name)
    if not kb:
        raise KnowledgeBaseEmptyError("知识库为空")
    docs = get_documents_by_kb(db, kb.id)

    doc_ids = [
        doc.id
        for doc in docs
    ]

    for doc in doc_ids:
        await file_delete(
            db,
            doc.id,
            kb.name
        )

    delete_kb(db, kb.id)
    return True

