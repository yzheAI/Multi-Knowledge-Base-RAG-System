import os
import uuid
from app.crud import knowledge_base, document_crud, chunk_crud
from app.tasks.document_task import process_document_task
from app.crud.task_crud import create_task
from app.knowledge_base.manager import KnowledgeManager
from app.config import SEARCH_TOP_K, KNOWLEDGE_BASE_PATH
from app.exceptions.exceptions import DocumentNotFound, KnowledgeBaseEmptyError
from app.core.container import container


async def upload(db, file, kb_name, owner_id):

    kdg = KnowledgeManager(KNOWLEDGE_BASE_PATH)

    kb = knowledge_base.get_kb_by_name(
        db,
        kb_name,
        owner_id
    )

    if not kb:
        raise KnowledgeBaseEmptyError()

    kb_path = kdg.get_path(
        kb_name,
        owner_id
    )

    # 上传整个文档至kb
    upload_dir = os.path.join(
        kb_path,
        "files"
    )

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    file_path = os.path.join(
        upload_dir,
        file.filename
    )

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 创建task
    task_id = str(uuid.uuid4())

    create_task(
        db,
        task_id,
        file.filename,
        owner_id
    )
    # 异步任务
    process_document_task.delay(
        task_id,
        file_path,
        file.filename,
        kb_name,
        owner_id
    )

    return {
        "task_id": task_id,
        "status": "pending"
    }


async def search_files(db, query: str, kb_name, owner_id):

    result = container.hybrid_retriever.retrieve(
        db,
        query,
        kb_name,
        owner_id,
        SEARCH_TOP_K
    )
    return result


async def get_all_files(
        db,
        kb_name,
        owner_id
):
    # 获取知识库信息
    kb = knowledge_base.get_kb_by_name(
        db,
        kb_name,
        owner_id
    )
    if not kb:
        raise KnowledgeBaseEmptyError()

    documents = document_crud.get_documents_by_kb(
        db,
        kb.id
    )

    return {
        "count": len(documents),
        "files": [
            {
                "doc_id": doc.id,
                "filename": doc.filename,
                "file_path": doc.file_path,
                "created_at": doc.created_at,
                "chunks": [
                    {
                        "id": chunk.id,
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "metadata": chunk.metadata_info
                    }
                    for chunk in chunk_crud.get_chunks_by_document_id(
                        db,
                        doc.id
                    )
                ]
            }
            for doc in documents
        ]
    }


async def file_delete(
        db,
        doc_id: int,
        kb_name: str,
        owner_id: int
):
    kdg = KnowledgeManager(
        KNOWLEDGE_BASE_PATH
    )

    document = document_crud.get_document_by_id(
        db,
        doc_id,
        owner_id
    )

    if not document:
        raise DocumentNotFound(
            message="文档不存在"
        )
    file_path = document.file_path

    store = container.vector_manager.get_store(
        kb_name,
        db,
        owner_id
    )

    kb_path = kdg.get_path(kb_name, owner_id)

    # 取出要删除的chunks，得到ids进行向量删除
    chunks = chunk_crud.get_chunks_by_document_id(
        db,
        doc_id
    )

    chunk_ids = [
        chunk.id
        for chunk in chunks
    ]

    if not chunk_ids:

        if os.path.exists(file_path):
            os.remove(file_path)

        document_crud.delete_document(
            db,
            doc_id,
            owner_id
        )

        return True

    # 删除向量
    success_flag = store.delete(
        chunk_ids,
        kb_path,
    )

    if not success_flag:
        raise DocumentNotFound(
            message="文档不存在"
        )

    # 删除 chunk
    chunk_crud.delete_chunks_by_document_id(
        db,
        document_id=doc_id
    )

    # 删除物理文件
    if os.path.exists(file_path):
        os.remove(file_path)

    # 删除数据库中文档
    document_crud.delete_document(
        db,
        doc_id,
        owner_id
    )

    return success_flag
