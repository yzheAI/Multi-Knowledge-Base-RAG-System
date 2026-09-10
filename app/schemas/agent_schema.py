from pydantic import BaseModel

from app.schemas.chat import MetadataFilter


class AgentRequest(BaseModel):
    query: str
    kb_name: str
    filters: MetadataFilter | None = None
