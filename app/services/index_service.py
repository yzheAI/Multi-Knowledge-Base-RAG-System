from sqlalchemy.orm import Session
from app.models.chunk import Chunk
from app.schemas.document_types import ChunkStatus
from app.crud.chunk_crud import get_failed_chunks
from app.embedding.embedding import get_embeddings


def index_chunks(
        db: Session,
        store,
        chunks: list[Chunk],
        vectors,
):
    if not chunks:
        return

    chunk_ids = [chunk.id for chunk in chunks]

    try:

        store.add(
            vectors,
            [chunk.content for chunk in chunks],
            chunk_ids=chunk_ids,
        )

        for chunk in chunks:
            chunk.status = ChunkStatus.INDEXED

        db.commit()

    except Exception:

        for chunk in chunks:
            chunk.status = ChunkStatus.FAILED

        db.commit()

        raise


def retry_failed_chunks(
        db: Session,
        store,
):
    chunks = get_failed_chunks(db)

    if not chunks:
        return 0

    for chunk in chunks:
        chunk.status = ChunkStatus.PENDING

    db.commit()

    texts = [chunk.content for chunk in chunks]

    vectors = get_embeddings(texts)

    index_chunks(
        db,
        store,
        chunks,
        vectors
    )

    return len(chunks)


def index_chunks_with_retry(
        db: Session,
        store,
        chunks,
        vectors,
        max_retries=3
):
    for attempt in range(max_retries):
        try:
            index_chunks(
                db=db,
                store=store,
                chunks=chunks,
                vectors=vectors,
            )

            return

        except Exception:
            if attempt == max_retries - 1:
                raise
