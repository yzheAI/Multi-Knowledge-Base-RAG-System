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
            owner_id,
            top_k=5,
            filters=None
    ):
        faiss_docs = self.faiss_retriever.retrieve(
            db,
            query,
            kb_name,
            owner_id,
            top_k,
            filters
        )

        bm25_docs = self.bm25_retriever.retrieve(
            db,
            query,
            kb_name,
            owner_id,
            top_k,
            filters
        )

        docs = self.merge(
            faiss_docs,
            bm25_docs
        )

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
            doc_chunk_id = doc["chunk_id"]
            if doc_chunk_id not in seen:
                seen.add(doc_chunk_id)
                result.append(doc)

        return result
