from sqlalchemy.orm import Session

from app.crud.knowledge_base import create_kb
import uuid


def generate_kb_name():
    return f"test_kb_{uuid.uuid4().hex}"


def test_create_kb(db: Session):
    kb_name = generate_kb_name()

    kb = create_kb(
        db,
        kb_name
    )

    assert kb.id is not None
    assert kb.name == kb_name
