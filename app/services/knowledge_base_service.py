from app.config import KNOWLEDGE_BASE_PATH
from app.crud.knowledge_base import get_kb_by_name, get_all_kbs, delete_kb
from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.knowledge_base.manager import KnowledgeManager
from app.crud.document_crud import get_documents_by_kb
import os
from app.core.container import container
from app.services.upload_service import file_delete
import shutil
from app.cache.retrieval_cache import RetrievalCache


async def create(db, kb_name, owner_id):

    kb = get_kb_by_name(
        db,
        kb_name,
        owner_id
    )
    if kb:
        return {
            "id": kb.id,
            "name": kb.name,
            "created_at": kb.created_at,
        }

    kdg = KnowledgeManager(KNOWLEDGE_BASE_PATH)

    kb = kdg.create(
        db,
        kb_name,
        owner_id
    )

    kb_path = kdg.get_path(kb_name, owner_id)

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
        "owner_id": owner_id,
        "created_at": kb.created_at,
    }


async def get_all_kb_service(db, owner_id):
    kbs = get_all_kbs(db, owner_id)
    result = [
        {
            "id": kb.id,
            "name": kb.name,
            "owner_id": kb.owner_id,
            "created_at": kb.created_at,
        }
        for kb in kbs
    ]
    return result


async def get_kb_service(db, kb_name, owner_id):
    kb = get_kb_by_name(db, kb_name, owner_id)
    if not kb:
        raise KnowledgeBaseEmptyError("无该知识库")

    docs = get_documents_by_kb(db, kb.id)

    return {
        "kb_id": kb.id,
        "kb_name": kb.name,
        "owner_id": kb.owner_id,
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


async def delete_kb_service(db, kb_name, owner_id):
    kb = get_kb_by_name(db, kb_name, owner_id)
    if not kb:
        raise KnowledgeBaseEmptyError("知识库为空")
    docs = get_documents_by_kb(db, kb.id)

    doc_ids = [
        doc.id
        for doc in docs
    ]

    for doc_id in doc_ids:
        await file_delete(
            db,
            doc_id,
            kb.name,
            owner_id
        )

    delete_kb(db, kb.id)

    kdg = KnowledgeManager(
        KNOWLEDGE_BASE_PATH
    )

    kb_path = kdg.get_path(kb_name, owner_id)

    if os.path.exists(kb_path):
        shutil.rmtree(kb_path)

    # 删除缓存
    container.vector_manager.remove_store(
        kb.name
    )

    retrieval_cache = RetrievalCache()
    retrieval_cache.delete_by_kb(
        owner_id,
        kb.id
    )

    return True
