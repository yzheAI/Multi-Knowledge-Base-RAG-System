from fastapi.testclient import TestClient
from main import app
import uuid


client = TestClient(app)


def test_get_files_api():

    kb_name = f"api_test_{uuid.uuid4().hex}"

    response = client.get(
        "/files/files_message",
        params={
            "kb_name": "copper_based"
        }
    )
    assert response.status_code == 200

    result = response.json()

    assert result["code"] == 200
    assert "count" in result["data"]
    assert "files" in result["data"]


def test_upload_and_get_files_api():

    kb_name = f"api_test_{uuid.uuid4().hex}"

    file = {
        "file": (
            "api_text.txt",
            "铜基复合材料是一种复合材料",
            "text/plain"
        )
    }

    data = {
        "kb_name": kb_name
    }

    upload_response = client.post(
        "/files",
        files=file,
        data=data
    )

    assert upload_response.status_code == 200

    response = client.get(
        "/files/files_message",
        params={
            "kb_name": kb_name
        },
    )

    result = response.json()

    assert result["data"]["count"] == 1

    assert (
        result["data"]["files"][0]["filename"]
        ==
        "api_text.txt"
    )


def test_delete_document_api():

    kb_name = f"api_test_{uuid.uuid4().hex}"

    file = {
        "file": (
            "delete_test.txt",
            "铜基复合材料是一种复合材料，具有良好的导电性能和机械性能，可以应用于工业制造领域。",
            "text/plain"
        )
    }

    data = {
        "kb_name": kb_name
    }

    upload_response = client.post(
        "/files/",
        files=file,
        data=data
    )

    result = upload_response.json()

    doc_id = result["data"]["document_id"]

    delete_response = client.delete(
        f"/files/{doc_id}",
        params={
            "kb_name": kb_name
        }
    )
    print("delete:", delete_response.json())
    assert delete_response.status_code == 200

    files_response = client.get(
        "/files/files_message",
        params={
            "kb_name": kb_name
        }
    )
    print("files:", files_response.json())

    files = files_response.json()["data"]

    assert files["count"] == 0



