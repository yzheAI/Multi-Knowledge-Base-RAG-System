from sqlalchemy.orm import Session

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
            chunk_index=index
        )
        db.add(chunk)
        chunk_object.append(chunk)

    db.commit()

    for chunk in chunk_object:
        db.refresh(chunk)

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
    chunks = get_chunks_by_document_id(
        db,
        document_id
    )

    if not chunks:
        return False

    for chunk in chunks:
        db.delete(chunk)
    db.commit()

    return True



