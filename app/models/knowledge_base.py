from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime

from sqlalchemy.orm import relationship

from app.database.session import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(255),
        unique=True,
        nullable=False
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    description = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    owner = relationship(
        "User",
        back_populates="knowledge_bases"
    )


knowledge_base = KnowledgeBase()

