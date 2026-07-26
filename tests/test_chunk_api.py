from fastapi.testclient import TestClient
from main import app
import uuid
from app.crud.chunk_crud import get_chunks_by_document_id
from app.database.session import SessionLocal

client = TestClient(app)


def generate_kb_name():
    return f"chunk_test_kb_{uuid.uuid4().hex}"


def test_chunk_api():
    file = {
        "file": (
            "chunk_test.txt",
            "铜基复合材料是..."
            "text/plain"
        )
    }

    data = {
        "kb_name": generate_kb_name(),
    }

    response = client.post(
        "/files/",
        files=file,
        data=data,
    )

    assert response.status_code == 200

    result = response.json()

    doc_id = result["data"]["document_id"]

    db = SessionLocal()

    try:
        chunks = get_chunks_by_document_id(
            db,
            doc_id
        )
        assert len(chunks) > 0

        assert chunks[0].document_id == doc_id

        assert chunks[0].chunk_index == 0
    finally:
        db.close()



