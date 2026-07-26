from sqlalchemy.orm import Session

from app.crud.chunk_crud import create_chunk, get_chunks_by_document_id, delete_chunks_by_document_id, create_chunks
from app.crud.document_crud import create_document
from app.crud.knowledge_base import create_kb
import uuid


def generate_kb_name():
    return f"test_kb_{uuid.uuid4().hex}"


def test_chunks_crud(db: Session):
    kb = create_kb(
        db,
        generate_kb_name(),
    )

    document = create_document(
        db,
        kb.id,
        "test.txt"
    )

    chunks = [
        "铜基复合材料是一种复合材料",
        "具有良好的导电性能和机械性能"
    ]

    result = create_chunks(
        db,
        document_id=document.id,
        chunks=chunks,
        metadata={
            "source": "test.txt",
            "file_type": ".txt"
        }
    )

    assert len(result) == 2
    assert result[0].content == chunks[0]
    assert result[0].chunk_index == 0
    assert result[1].chunk_index == 1


def test_get_chunks_by_document(db: Session):

    kb = create_kb(
        db,
        generate_kb_name(),
    )

    doc = create_document(
        db,
        kb.id,
        "demo.txt"
    )

    create_chunks(
        db,
        doc.id,
        [
            "第一段内容",
            "第二段内容",
            "第三段内容"
        ],
        {
            "source": "demo.txt"
        }
    )

    chunks = get_chunks_by_document_id(
        db,
        doc.id,
    )

    assert len(chunks) == 3

    assert chunks[0].content == "第一段内容"
    assert chunks[0].chunk_index == 0


def test_delete_chunks_by_document(db: Session):
    kb = create_kb(
        db,
        generate_kb_name(),
    )

    doc = create_document(
        db,
        kb.id,
        "delete.txt"
    )

    create_chunks(
        db,
        doc.id,
        [
            "需要删除的chunk1",
            "需要删除的chunk2"
        ],
        {
            "source": "delete.txt"
        }
    )

    chunks = get_chunks_by_document_id(
        db,
        doc.id,
    )

    assert len(chunks) == 2

    delete_chunks_by_document_id(
        db,
        doc.id,
    )

    chunks = get_chunks_by_document_id(
        db,
        doc.id,
    )

    assert len(chunks) == 0

