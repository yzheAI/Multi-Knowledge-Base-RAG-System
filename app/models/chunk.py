from sqlalchemy import Column, Integer, Text, ForeignKey, JSON, String

from app.database.session import Base
from app.schemas.document_types import ChunkStatus


class Chunk(Base):
    __tablename__ = 'chunk'

    id = Column(
        Integer,
        primary_key=True
    )

    document_id = Column(
        Integer,
        ForeignKey('document.id'),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    chunk_index = Column(
        Integer,
        nullable=False
    )

    metadata_info = Column(
        JSON,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=True,
        default=ChunkStatus.PENDING,
        index=True
    )
