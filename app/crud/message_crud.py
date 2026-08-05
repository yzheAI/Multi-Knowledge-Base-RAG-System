from app.models.conversation import Conversation
from app.models.message import Message
from sqlalchemy.orm import Session


def create_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
):
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_messages_by_conversation_id(
        db: Session,
        conversation_id: str,
        user_id: int,
):
    messages = (
        db.query(Message)
        .join(Conversation)
        .filter(
            Message.conversation_id == conversation_id,
            Conversation.user_id == user_id,
        ).order_by(
            Message.id.asc()
        ).all()
    )
    return messages
