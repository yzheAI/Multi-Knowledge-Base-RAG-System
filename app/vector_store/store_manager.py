from app.config import KNOWLEDGE_BASE_PATH, EMBEDDING_DIM
from app.knowledge_base.manager import KnowledgeManager
from app.vector_store.faiss_store import VectorStore
from app.crud.knowledge_base import get_kb_by_name


class VectorStoreManager:
    def __init__(self):
        self.stores = {}
        self.kb_manager = KnowledgeManager(
            KNOWLEDGE_BASE_PATH
        )

    def get_store(self, kb_name, db):

        if kb_name not in self.stores:

            store = VectorStore(EMBEDDING_DIM)

            kb_path = self.kb_manager.get_path(
                kb_name=kb_name
            )

            kb = get_kb_by_name(
                db,
                name=kb_name,
            )

            store.load(
                f"{kb_path}/faiss.index",
                kb_id=kb.id,
                db=db
            )

            self.stores[kb_name] = store

        return self.stores[kb_name]
