from app.models.knowledge_base import KnowledgeBase
from sqlalchemy.orm import Session


def create_kb(
        db: Session,
        name: str,
        description: str = None,
):
    kb = KnowledgeBase(
        name=name,
        description=description
    )

    db.add(kb)
    db.commit()
    db.refresh(kb)

    return kb


def get_kb_by_id(
        db: Session,
        kb_id: int,
):
    kb = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id == kb_id
        ).first()
    )

    return kb


def get_kb_by_name(
        db: Session,
        name: str,
):
    kb = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.name == name
        ).first()
    )
    return kb


def get_all_kbs(
        db: Session,
):
    return db.query(
        KnowledgeBase
    ).all()


def delete_kb(
        db: Session,
        kb_id: int
):
    kb = get_kb_by_id(
        db,
        kb_id
    )

    if not kb:
        return False

    if kb:
        db.delete(kb)
        db.commit()
    return True

