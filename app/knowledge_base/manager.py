import os
from app.crud import knowledge_base


class KnowledgeManager:
    def __init__(self, base_path):
        self.base_path = base_path

    def create(
            self,
            db,
            name,
            description=None,
    ):
        kb = knowledge_base.create_kb(
            db,
            name,
            description,
        )

        return kb

    def get_path(self, kb_name):
        return os.path.join(
            self.base_path,
            kb_name
        )

    def list(self, db):
        return knowledge_base.get_all_kbs(db)
