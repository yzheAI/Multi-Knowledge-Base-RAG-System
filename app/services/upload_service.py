import os
from datetime import datetime
from app.knowledge_base.manager import KnowledgeManager
from app.config import SEARCH_TOP_K, KNOWLEDGE_BASE_PATH
from app.document.pipeline import process_document
from app.embedding.embedding import get_embedding
from app.exceptions.exceptions import DocumentNotFound, KnowledgeBaseEmptyError
from app.core.container import container
from app.crud import document_crud, knowledge_base, chunk_crud


async def upload(db, file, kb_name):
    # 获取知识库
    kdg = KnowledgeManager(KNOWLEDGE_BASE_PATH)

    kb = knowledge_base.get_kb_by_name(
        db,
        kb_name
    )

    if not kb:
        kb = kdg.create(
            db,
            kb_name
        )
    # 获取上传文件路径
    kb_path = kdg.get_path(
        kb_name
    )

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
    # 上传文档至目标文件夹
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # 获取信息
    result = process_document(
        str(file_path)
    )

    # 上传文档至SQL
    doc = document_crud.create_document(
        db=db,
        kb_id=kb.id,
        filename=file.filename,
        file_path=file_path,
    )

    metadata = result["metadata"]

    metadata.update({
        "source": file.filename,
        "upload_time": datetime.now().isoformat()
    })

    chunk_crud.create_chunks(
        db=db,
        document_id=doc.id,
        chunks=result["chunks"],
        metadata=metadata
    )

    store = container.vector_manager.get_store(
        kb_name
    )
    store.add(
        result["vectors"],
        result["chunks"],
        doc_id=str(doc.id),
        metadata=metadata
    )

    store.save(
        kb_path
    )

    return {
        "filename": file.filename,
        "document_id": doc.id,
        "msg": "上传成功",
        "analysis": result
    }


async def search_files(query: str, kb_name):
    store = container.vector_manager.get_store(
        kb_name
    )

    if not store.data:
        raise KnowledgeBaseEmptyError()

    query_embedding = get_embedding(query)

    result = store.search(
        query_embedding,
        top_k=SEARCH_TOP_K
    )
    return result


async def get_all_files(
        db,
        kb_name
):
    # 获取知识库信息
    kb = knowledge_base.get_kb_by_name(
        db,
        kb_name
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
            }
            for doc in documents
        ]
    }


async def file_delete(db,
                      doc_id: int,
                      kb_name: str
                      ):
    kdg = KnowledgeManager(
        KNOWLEDGE_BASE_PATH
    )

    store = container.vector_manager.get_store(
        kb_name
    )

    kb_path = kdg.get_path(
        kb_name
    )

    # 删除向量
    success_flag = store.delete(
        str(doc_id),
        kb_path
    )

    if not success_flag:
        raise DocumentNotFound(
            message="文档不存在"
        )

    # 删除数据库中文档
    document_crud.delete_document(
        db,
        doc_id
    )

    return success_flag
