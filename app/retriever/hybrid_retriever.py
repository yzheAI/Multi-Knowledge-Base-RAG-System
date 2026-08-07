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

        candidate_k = 20

        faiss_docs = self.faiss_retriever.retrieve(
            db,
            query,
            kb_name,
            owner_id,
            candidate_k,
            filters
        )

        bm25_docs = self.bm25_retriever.retrieve(
            db,
            query,
            kb_name,
            owner_id,
            candidate_k,
            filters
        )

        # docs = self.merge(
        #     faiss_docs,
        #     bm25_docs
        # )
        docs = self.rrf_fusion(
            faiss_docs,
            bm25_docs
        )

        results = self.reranker.rank(
            query,
            docs[:candidate_k]
        )

        return results[:top_k]

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

    def rrf_fusion(
            self,
            faiss_docs,
            bm25_docs,
            k=40
    ):
        scores = {}

        docs_map = {}

        for rank, doc in enumerate(
                faiss_docs,
                start=1
        ):

            chunk_id = doc["chunk_id"]

            scores[chunk_id] = (
                scores.get(chunk_id, 0)
                +
                1 / (k + rank)
            )

            docs_map[chunk_id] = doc

        for rank, doc in enumerate(
                bm25_docs,
                start=1
        ):

            chunk_id = doc["chunk_id"]

            scores[chunk_id] = (
                scores.get(chunk_id, 0)
                +
                1/(k + rank)
            )

            docs_map[chunk_id] = doc

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            docs_map[chunk_id]
            for chunk_id, scores in ranked
        ]
