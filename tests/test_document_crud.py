from sqlalchemy.orm import Session
from app.crud.document_crud import (create_document, delete_document, get_document_by_id, get_all_documents,
                                    get_documents_by_kb)
from app.crud.knowledge_base import create_kb
import uuid


def generate_kb_name():
    return f"test_kb_{uuid.uuid4().hex}"


def test_create_document(db: Session):
    name = f"test_kb_{uuid.uuid4().hex}"
    kb = create_kb(
        db,
        generate_kb_name()
    )

    doc = create_document(
        db,
        kb.id,
        "test.pdf",
        "/data/test.pdf"
    )
    assert doc.id is not None
    assert doc.filename == "test.pdf"


def test_get_document(db: Session):
    kb = create_kb(
        db,
        generate_kb_name()
    )
    doc = create_document(
        db,
        kb.id,
        "demo.pdf",
    )
    result = get_document_by_id(
        db,
        doc.id
    )
    assert result.filename == "demo.pdf"


def test_get_documents_by_kb(db: Session):
    kb = create_kb(
        db,
        generate_kb_name()
    )
    create_document(
        db,
        kb.id,
        "a.pdf",
    )

    create_document(
        db,
        kb.id,
        "b.pdf"
    )

    docs = get_documents_by_kb(
        db,
        kb.id,
    )
    assert len(docs) == 2


def test_delete_document(db: Session):
    kb = create_kb(
        db,
        generate_kb_name()
    )

    doc = create_document(
        db,
        kb.id,
        "delete.pdf"
    )

    result = delete_document(
        db,
        doc.id
    )

    assert result is True

    assert get_document_by_id(
        db,
        doc.id
    ) is None
