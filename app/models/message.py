from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from app.database.session import Base


class Message(Base):
    __tablename__ = 'messages'
    id = Column(
        Integer,
        primary_key=True
    )

    conversation_id = Column(
        String(128),
        ForeignKey(
            'conversation.conversation_id'
        ),
        index=True
    )
    role = Column(
        String(20)
    )

    content = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
