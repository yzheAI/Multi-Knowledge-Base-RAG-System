from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database.session import Base


class Document(Base):
    __tablename__ = "document"

    id = Column(
        Integer,
        primary_key=True
    )

    kb_id = Column(
        Integer,
        ForeignKey("knowledge_base.id"),
        nullable=False
    )

    filename = Column(
        String(255),
        nullable=False
    )

    document_type = Column(
        String(50),
        nullable=True
    )

    file_path = Column(
        String(500)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
