from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime

from sqlalchemy.orm import relationship

from app.database.session import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    __table_args__ = (
        UniqueConstraint(
            'owner_id',
            'name',
            name='uq_owner_kb_name'
        ),
    )

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(255),
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


