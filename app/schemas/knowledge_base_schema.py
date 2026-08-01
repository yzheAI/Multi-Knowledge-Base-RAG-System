from pydantic import BaseModel


class KnowledgeBaseCreate(BaseModel):
    name: str