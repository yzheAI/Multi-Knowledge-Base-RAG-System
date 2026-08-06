from sqlalchemy.orm import Session
import uuid

from app.exceptions.exceptions import ConversationNotFound
from app.models.conversation import Conversation
from app.models.message import Message


def get_conversation_id():
    return f"conversation_{uuid.uuid4().hex}"


def create_conversation(
        db: Session,
        user_id: int,
        kb_id: int,
        title: str
):
    conversation_id = get_conversation_id()

    conversation = Conversation(
        user_id=user_id,
        kb_id=kb_id,
        title=title,
        conversation_id=conversation_id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(
        db: Session,
        conversation_id: str,
        user_id: int
):
    conversation = (
        db.query(
            Conversation
        ).filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id
        ).first()
    )
    if not conversation:
        raise ConversationNotFound()

    return conversation


def delete_conversation(
        db: Session,
        conversation_id: str,
        user_id: int
):
    conversation = get_conversation(
        db,
        conversation_id,
        user_id
    )

    db.query(Message).filter(
        Message.conversation_id == conversation_id,
    ).delete(
        synchronize_session=False
    )

    db.delete(conversation)
    db.commit()
    return True


def get_user_conversations(
        db: Session,
        user_id: int,
        kb_id: int = None
):
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.user_id == user_id,
        )
    )

    if kb_id:
        conversations = conversations.filter(
            Conversation.kb_id == kb_id
        )
    return conversations.order_by(
        Conversation.created_at.desc()
    ).all()


def update_conversation_title(
        db,
        conversation_id,
        title
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == conversation_id,
        )
        .first()
    )

    conversation.title = title

    db.commit()
    db.refresh(conversation)
