from app.crud import chunk_crud
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

        hits = store.search(
            embedding,
            top_k,
        )

        chunk_ids = [
            h["chunk_id"]
            for h in hits
        ]

        chunks = chunk_crud.get_chunks_by_ids(
            db,
            chunk_ids,
        )

        chunk_map = {
            chunk.id: chunk
            for chunk in chunks
        }

        results = []

        for hit in hits:
            chunk = chunk_map.get(
                hit["chunk_id"]
            )

            if chunk is None:
                continue

            if filters is not None:
                matched = all(
                    chunk.metadata_info.get(k) == v
                    for k, v in filters.items()
                )

                if not matched:
                    continue

            results.append({
                "text": chunk.content,
                "chunk_id": chunk.id,
                "score": hit["score"],
                "source": "faiss",
                "metadata": chunk.metadata_info
            })

        return results
