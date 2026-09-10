from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.database.session import Base
from app.tasks.status import TaskStatus


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(
        Integer,
        primary_key=True,
    )

    task_id = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    filename = Column(
        String(255),
        nullable=False,
    )

    document_type = Column(
        String(50),
        nullable=False,
    )

    owner_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    kb_id = Column(
        Integer,
        ForeignKey('knowledge_base.id'),
        nullable=False,
        index=True
    )

    file_path = Column(
        String(500),
        nullable=False,
    )

    kb_path = Column(
        String(500),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )

    progress = Column(
        Integer,
        nullable=False,
        default=0
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    error_message = Column(Text)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )
