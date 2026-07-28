from app.crud import chunk_crud
from app.exceptions.exceptions import KnowledgeBaseEmptyError
from app.retriever.base import BaseRetriever


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
            top_k=5,
            filters=None
    ):
        store = self.vector_manager.get_store(
            kb_name,
            db
        )

        if store is None:
            raise KnowledgeBaseEmptyError(
                "知识库不存在"
            )
        # 查找到最符合的chunks信息
        hits = store.bm25.search(
            query,
            top_k
        )

        results = []

        chunk_ids = [
            hit["chunk_id"]
            for hit in hits
        ]

        chunks = chunk_crud.get_chunks_by_ids(
            db,
            chunk_ids
        )

        chunk_map = {
            chunk.id: chunk
            for chunk in chunks
        }

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
                "source": "bm25",
                "metadata": chunk.metadata_info
            })
        return results
