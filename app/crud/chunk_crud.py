from sqlalchemy.orm import Session
from app.schemas.document_types import ChunkStatus
from app.models import Document
from app.models.chunk import Chunk


def create_chunk(
        db: Session,
        document_id: int,
        content: str,
        chunk_index: int,
        metadata: dict
):
    chunk = Chunk(
        document_id=document_id,
        content=content,
        chunk_index=chunk_index,
        metadata_info=metadata
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


def create_chunks(
        db: Session,
        document_id: int,
        chunks: list[str],
        metadata: dict
):

    chunk_object = []
    for index, content in enumerate(chunks):
        chunk = Chunk(
            document_id=document_id,
            content=content,
            metadata_info=metadata,
            chunk_index=index,
            status=ChunkStatus.PENDING
        )

        chunk_object.append(chunk)

    db.add_all(chunk_object)
    db.commit()

    return chunk_object


def get_chunks_by_document_id(
        db: Session,
        document_id: int,
):
    chunks = db.query(
        Chunk
    ).filter(
        Chunk.document_id == document_id
    ).all()

    return chunks


def delete_chunks_by_document_id(
        db: Session,
        document_id: int,
):
    deleted_count = (
        db.query(Chunk)
        .filter(Chunk.document_id == document_id)
        .delete(synchronize_session=False)
    )

    db.commit()

    return deleted_count > 0


def get_all_chunks_by_kb(
        db: Session,
        kb_id
):
    chunks = (
        db.query(Chunk)
        .join(Document)
        .filter(
            Document.kb_id == kb_id
        )
        .all()
    )

    return chunks


def get_chunks_by_ids(
        db: Session,
        chunk_ids: list[int]
):
    return (
        db.query(Chunk)
        .filter(
            Chunk.id.in_(chunk_ids),  # 批量查询指定chunk_id的数据
            Chunk.status == ChunkStatus.INDEXED
        )
        .all()
    )


def get_failed_chunks(
        db: Session,
):
    chunks = db.query(
        Chunk
    ).filter(
        Chunk.status == ChunkStatus.FAILED
    ).all()

    return chunks
