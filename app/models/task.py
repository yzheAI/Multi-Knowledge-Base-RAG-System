from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    task_id = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    filename = Column(
        String(255),
    )

    owner_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )

    status = Column(
        String(50),
        default='pending',
    )

    error_message = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )
