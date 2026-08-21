from datetime import datetime

from app.cache.retrieval_cache import RetrievalCache
from app.core.container import container
from app.crud import task_crud, knowledge_base, document_crud, chunk_crud
from app.document.pipeline import process_document
from app.exceptions.exceptions import KnowledgeBaseEmptyError


def handle_document_upload(
        db,
        task_id,
        file_path,
        kb_path,
        filename,
        kb_name,
        owner_id
):
    # 更新状态
    task_crud.update_task_status(
        db,
        task_id,
        "processing",
        owner_id
    )

    # 获取知识库
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

    store.save(kb_path)

    container.vector_manager.remove_store(
        kb_name,
        owner_id
    )

    # 删除Retrieval缓存
    retrieval_cache = RetrievalCache()

    retrieval_cache.delete_by_kb(
        owner_id,
        kb.id
    )

    task_crud.update_task_status(
        db,
        task_id,
        "success",
        owner_id
    )
