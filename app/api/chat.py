from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.schemas.chat import ChatRequest
from app.services.chat_service_stream import chat_service_stream

chat_router = APIRouter(prefix="/chat", tags=["chat"])


@chat_router.post("/chat/stream")
async def chat(
        request: ChatRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
):
    return StreamingResponse(
        chat_service_stream(
            db=db,
            query=request.query,
            kb_name=request.kb_name,
            conversation_id=request.conversation_id,
            filters=request.filters,
            owner_id=current_user.id,
        ),
        media_type="text/event-stream",
    )

