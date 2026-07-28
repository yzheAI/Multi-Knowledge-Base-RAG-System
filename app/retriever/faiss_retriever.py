from app.embedding.embedding import get_embedding
from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.retriever.base import BaseRetriever


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
            top_k=5,
            filters=None
    ):
        store = self.vector_manager.get_store(
            kb_name,
            db
        )

        if store is None:
            raise KnowledgeBaseEmptyError("知识库不存在")

        embedding = get_embedding(
            query
        )

        result = store.search(
            embedding,
            top_k,
        )

        return result
