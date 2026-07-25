from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
        db: Session,
        kb_id: int,
        filename: str,
        file_path: str = None
):
    document = Document(
        kb_id=kb_id,
        filename=filename,
        file_path=file_path
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def delete_document(
        db: Session,
        document_id: int,
):
    document = get_document_by_id(
        db,
        document_id
    )
    if not document:
        return False

    db.delete(document)
    db.commit()
    return True


def get_document_by_id(
        db: Session,
        document_id: int,
):
        doc = db.query(
            Document
        ).filter(
            Document.id == document_id
        ).first()

        return doc


def get_documents_by_kb(
        db: Session,
        kb_id: int,
):
    docs = (
        db.query(Document)
        .filter(
            Document.kb_id == kb_id
        )
        .all()
    )
    return docs


def get_all_documents(
        db: Session,
):
    docs = db.query(
        Document
    ).all()

    return docs
