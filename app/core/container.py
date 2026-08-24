from app.vector_store.store_manager import VectorStoreManager
from app.retriever.faiss_retriever import FaissRetriever
from app.retriever.bm25_retriever import BM25Retriever
from app.retriever.hybrid_retriever import HybridRetriever
from app.retriever.reranker import CrossEncoderReranker


class Container:
    def __init__(self):
        self.vector_manager = VectorStoreManager()

        self.faiss_retriever = FaissRetriever(
            self.vector_manager,
        )

        self.bm25_retriever = BM25Retriever(
            self.vector_manager,
        )

        self.reranker = CrossEncoderReranker()

        self.hybrid_retriever = HybridRetriever(
            self.faiss_retriever,
            self.bm25_retriever,
            self.reranker
        )


container = Container()

