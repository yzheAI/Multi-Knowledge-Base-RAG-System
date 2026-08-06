from datetime import datetime

from sqlalchemy import Integer, String, Column, DateTime, ForeignKey

from app.database.session import Base


class Conversation(Base):
    __tablename__ = 'conversation'
    id = Column(
        Integer,
        primary_key=True
    )

    conversation_id = Column(
        String(128),
        unique=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey(
            'users.id'
        ),
    )

    kb_id = Column(
        Integer,
        ForeignKey(
            'knowledge_base.id'
        )
    )

    title = Column(
        String(255),
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )
