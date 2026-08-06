from pydantic import BaseModel


class SourceResponse(BaseModel):
    content: str
    score: float
    metadata: dict


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[SourceResponse]


class MetadataFilter(BaseModel):
    file_type: str | None = None
    source: str | None = None


class ChatRequest(BaseModel):
    query: str
    kb_name: str
    conversation_id: str | None = None
    filters: MetadataFilter | None = None
