from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.retriever.base import BaseRetriever
from app.retriever.utils import build_retriever_results
from app.crud import chunk_crud


class BM25Retriever(BaseRetriever):
    def __init__(
            self,
            vector_manager
    ):
        self.vector_manager = vector_manager

    def retrieve(
            self,
            db,
            query: str,
            kb_name: str,
            owner_id: int,
            top_k=10,
            filters=None,
            document_id=None
    ):
        store = self.vector_manager.get_store(
            kb_name,
            db,
            owner_id
        )

        if store is None:
            raise KnowledgeBaseEmptyError(
                "知识库不存在"
            )

        allowed_chunk_ids = None

        if document_id is not None:
            chunks = chunk_crud.get_chunks_by_document_id(
                db,
                document_id
            )

            allowed_chunk_ids = {
                chunk.id for chunk in chunks
            }

        # 查找到最符合的chunks信息
        hits = store.bm25.search(
            query,
            top_k,
            allowed_chunk_ids=allowed_chunk_ids
        )

        results = build_retriever_results(
            db,
            hits,
            "bm25",
            filters
        )

        return results
