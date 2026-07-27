from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.rag_service import chat_service_stream

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post("/chat/stream")
async def chat(request: ChatRequest):
    return StreamingResponse(
        chat_service_stream(
            query=request.query,
            kb_name=request.kb_name,
            filters=request.filters
        ),
        media_type="text/event-stream",
    )

