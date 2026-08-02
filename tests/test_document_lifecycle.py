from fastapi.testclient import TestClient
from main import app
import uuid
import os

client = TestClient(app)


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

    upload_data = upload_response.json()

    doc_id = upload_data["data"]["document_id"]

    response = client.get(
        "/files/files_message",
        params={
            "kb_name": kb_name
        },
    )
    assert response.status_code == 200

    result = response.json()

    assert result["data"]["count"] == 1

    document = result["data"]["files"][0]

    assert document["filename"] == "api_text.txt"

    # 文件存在
    file_path = document["file_path"]

    assert os.path.exists(file_path)

    # 删除文档
    delete_response = client.delete(
        f"/files/{doc_id}",
        params={
            "kb_name": kb_name
        }
    )

    assert delete_response.status_code == 200

    files_response = client.get(
        "/files/files_message",
        params={
            "kb_name": kb_name
        }
    )

    files = files_response.json()["data"]

    assert files["count"] == 0

    # 文件被删除
    assert not os.path.exists(file_path)


