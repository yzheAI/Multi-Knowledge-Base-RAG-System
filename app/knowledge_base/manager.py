import os
from app.crud import knowledge_base


class KnowledgeManager:
    def __init__(self, base_path):
        self.base_path = base_path

    def create(
            self,
            db,
            name,
            owner_id,
            description=None,
    ):
        kb = knowledge_base.create_kb(
            db,
            name,
            owner_id,
            description,
        )

        return kb

    def get_path(self, kb_id, owner_id):
        return os.path.join(
            self.base_path,
            str(owner_id),
            str(kb_id)
        )

    def list(self, db, owner_id):
        return knowledge_base.get_all_kbs(
            db,
            owner_id
        )
