from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database.session import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    knowledge_bases = relationship(
        "KnowledgeBase",
        back_populates="owner",
    )

