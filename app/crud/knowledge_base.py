from app.models.knowledge_base import KnowledgeBase
from sqlalchemy.orm import Session


def create_kb(
        db: Session,
        name: str,
        owner_id: int,
        description: str = None,
):
    kb = KnowledgeBase(
        name=name,
        owner_id=owner_id,
        description=description,
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
        owner_id
):
    kb = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.name == name,
            KnowledgeBase.owner_id == owner_id
        ).first()
    )
    return kb


def get_all_kbs(
        db: Session,
        owner_id
):
    return db.query(
        KnowledgeBase
    ).filter(
        KnowledgeBase.owner_id == owner_id
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

