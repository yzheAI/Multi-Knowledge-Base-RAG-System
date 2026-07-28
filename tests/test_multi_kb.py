from sqlalchemy.orm import Session
from app.crud import document_crud
from app.core.container import container
from app.embedding.embedding import get_embedding
from app.crud import knowledge_base, chunk_crud
import uuid


def test_multi_kb_isolation(db: Session):
    copper_name = f"copper_{uuid.uuid4().hex}"
    medical_name = f"medical_{uuid.uuid4().hex}"

    copper_kb = knowledge_base.create_kb(
        db,
        name=copper_name
    )

    medical_kb = knowledge_base.create_kb(
        db,
        name=medical_name
    )
    copper_store = container.vector_manager.get_store(
        copper_name,
        db=db
    )
    medical_store = container.vector_manager.get_store(
        medical_name,
        db=db
    )

    assert copper_store is not medical_store
