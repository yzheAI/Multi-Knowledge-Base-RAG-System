from app.crud import chunk_crud
from app.embedding.embedding import get_embedding
from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.retriever.base import BaseRetriever
from app.retriever.utils import build_retriever_results


class FaissRetriever(BaseRetriever):
    def __init__(
            self,
            vector_manager
    ):
        self.vector_manager = vector_manager

    def retrieve(
            self,
            db,
            query,
            kb_name,
            owner_id,
            top_k=10,
            filters=None,
            document_id=None,
    ):
        # 通过向量库查找到最相近的向量内容：hits
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

        embedding = get_embedding(query)

        hits = store.search(
            embedding,
            top_k,
            allowed_chunk_ids=allowed_chunk_ids
        )

        results = build_retriever_results(
            db,
            hits,
            "faiss",
            filters
        )

        return results
