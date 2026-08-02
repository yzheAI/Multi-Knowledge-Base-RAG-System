import os
from datetime import datetime
from app.knowledge_base.manager import KnowledgeManager
from app.config import SEARCH_TOP_K, KNOWLEDGE_BASE_PATH
from app.document.pipeline import process_document
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
    # 保存文件到知识库目录
    kb_path = kdg.get_path(kb_name)

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

    # 获取信息(chunks,vector,metadata)
    result = process_document(
        str(file_path)
    )

    # 上传文档信息至SQL
    doc = document_crud.create_document(
        db=db,
        kb_id=kb.id,
        filename=file.filename,
        file_path=file_path,
    )
    # 构建metadata，存入chunks，上传至SQL
    metadata = result["metadata"]

    metadata.update({
        "source": file.filename,
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
        db
    )
    store.add(
        result["vectors"],
        result["chunks"],
        chunk_ids=chunk_ids,
    )

    store.save(kb_path)

    container.vector_manager.remove_store(kb_name)

    return {
        "filename": file.filename,
        "document_id": doc.id,
        "msg": "上传成功",
        "analysis": result
    }


async def search_files(db, query: str, kb_name):

    result = container.hybrid_retriever.retrieve(
        db,
        query,
        kb_name,
        SEARCH_TOP_K
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
        kb_name: str
):
    kdg = KnowledgeManager(
        KNOWLEDGE_BASE_PATH
    )

    document = document_crud.get_document_by_id(
        db,
        doc_id
    )

    if not document:
        raise DocumentNotFound(
            message="文档不存在"
        )
    file_path = document.file_path

    store = container.vector_manager.get_store(
        kb_name,
        db
    )

    kb_path = kdg.get_path(kb_name)

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
            doc_id
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
    )

    return success_flag
