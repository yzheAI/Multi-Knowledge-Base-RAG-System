from app.crud import chunk_crud
from app.retriever.base import BaseRetriever


class HybridRetriever(BaseRetriever):
    def __init__(
        self,
        faiss_retriever,
        bm25_retriever,
        reranker
    ):
        self.faiss_retriever = faiss_retriever
        self.bm25_retriever = bm25_retriever
        self.reranker = reranker

    def retrieve(
            self,
            db,
            query,
            kb_name,
            top_k=5,
            filters=None
    ):
        faiss_docs = self.faiss_retriever.retrieve(
            db,
            query,
            kb_name,
            top_k,
            filters
        )

        bm25_docs = self.bm25_retriever.retrieve(
            db,
            query,
            kb_name,
            top_k,
            filters
        )

        docs = self.merge(
            faiss_docs,
            bm25_docs
        )
        # 根据chunk_id补充文本
        chunk_ids = [
            doc["chunk_id"]
            for doc in docs
        ]

        chunks = chunk_crud.get_chunks_by_ids(
            db,
            chunk_ids,
        )

        chunk_map = {
            chunk.id: chunk
            for chunk in chunks
        }
        for doc in docs:
            chunk = chunk_map.get(
                doc["chunk_id"],
            )
            if chunk:
                doc["text"] = chunk.content
                doc["metadata"] = chunk.metadata

        results = self.reranker.rank(
            query,
            docs
        )

        return results

    def merge(self, faiss_docs, bm25_docs):
        result = []
        seen = set()
        docs = faiss_docs + bm25_docs
        for doc in docs:
            doc_text = doc["chunk_id"]
            if doc_text not in seen:
                seen.add(doc_text)
                result.append(doc)

        return result
