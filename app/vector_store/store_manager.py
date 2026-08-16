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

    def get_store(
            self,
            kb_name,
            db,
            owner_id
    ):
        store_key = f"{owner_id}_{kb_name}"

        if store_key not in self.stores:

            store = VectorStore(EMBEDDING_DIM)

            kb_path = self.kb_manager.get_path(
                owner_id=owner_id,
                kb_name=kb_name
            )

            kb = get_kb_by_name(
                db,
                name=kb_name,
                owner_id=owner_id
            )

            if kb is None:
                return None

            store.load(
                f"{kb_path}/faiss.index",
                kb_path
            )

            self.stores[store_key] = store

        return self.stores[store_key]

    def remove_store(
            self,
            kb_name,
            owner_id
    ):
        store_key = f"{owner_id}_{kb_name}"

        if store_key in self.stores:
            del self.stores[store_key]
