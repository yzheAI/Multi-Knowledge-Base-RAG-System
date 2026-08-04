from fastapi.testclient import TestClient
from app.core.container import container
from app.config import KNOWLEDGE_BASE_PATH
from app.knowledge_base.manager import KnowledgeManager
from main import app
import uuid
import os
client = TestClient(app)


def get_auth_headers():
    username = f"test_{uuid.uuid4().hex}"
    password = "123456"

    register = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
        }
    )

    assert register.status_code == 200

    login = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        }
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }, login.json()["user_id"]


def test_knowledge_base_lifecycle():

    headers, user_id = get_auth_headers()

    kb_name = f"test_kb_{uuid.uuid4().hex}"

    try:
        # 创建知识库
        create_response = client.post(
            "/knowledge_bases",
            headers=headers,
            json={
                "name": kb_name,
                "description": "Test Knowledge Base",
            }
        )

        assert create_response.status_code == 200

        create_data = create_response.json()

        assert create_data["data"]["name"] == kb_name

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
            data=data,
            headers=headers
        )

        assert upload_response.status_code == 200

        response = client.get(
            "/files/files_message",
            params={
                "kb_name": kb_name
            },
            headers=headers
        )

        result = response.json()

        assert result["data"]["count"] == 1

        assert (
                result["data"]["files"][0]["filename"]
                ==
                "api_text.txt"
        )

        assert kb_name not in container.vector_manager.stores

        # 证明文件存在
        file_path = result["data"]["files"][0]["file_path"]

        assert os.path.exists(file_path)

        # 删除后缓存清理
        assert kb_name not in container.vector_manager.stores

        # 获取知识库信息

        get_response = client.get(
            f"/knowledge_bases/{kb_name}",
            headers=headers
        )

        assert get_response.status_code == 200

        get_data = get_response.json()

        assert get_data["data"]["kb_name"] == kb_name

        # 获取所有知识库

        get_all_response = client.get(
            "/knowledge_bases/all",
            headers=headers
        )

        assert get_all_response.status_code == 200

        all_data = get_all_response.json()

        names = [
            item["name"]
            for item in all_data["data"]
        ]

        assert kb_name in names

        # 删除知识库

        delete_response = client.delete(
            f"/knowledge_bases/{kb_name}",
            headers=headers
        )

        assert delete_response.status_code == 200

        # 证明已删除

        assert kb_name not in container.vector_manager.stores

        assert not os.path.exists(file_path)

        verify_response = client.get(
            f"/knowledge_bases/{kb_name}",
            headers=headers
        )

        assert verify_response.status_code == 404

        kdg = KnowledgeManager(
            KNOWLEDGE_BASE_PATH
        )

        kb_path = kdg.get_path(kb_name, user_id)

        assert not os.path.exists(kb_path)

    finally:
        # 确保清理
        try:
            client.delete(
                f"/knowledge_bases/{kb_name}",
                headers=headers
            )
        except Exception:
            pass
