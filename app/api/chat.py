from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.schemas.chat import ChatRequest
from app.services.chat_service_stream import chat_service_stream
from app.services.conversation_service import get_conversations_by_kb_service, \
    create_conversation_service, get_messages_service

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


@chat_router.post("/create_conversation")
async def create_conversation(
        kb_name: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
):
    conversation = create_conversation_service(
        kb_name=kb_name,
        db=db,
        user_id=current_user.id,
    )
    return conversation


@chat_router.get("/conversations")
async def get_conversations(
        kb_name: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
):
    conversations = get_conversations_by_kb_service(
        db=db,
        user_id=current_user.id,
        kb_name=kb_name,
    )

    return conversations


@chat_router.get("/messages/{conversation_id}")
async def get_messages(
        conversation_id: str,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    messages = get_messages_service(
        db,
        conversation_id,
        current_user.id
    )

    return messages
