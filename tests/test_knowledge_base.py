from fastapi.testclient import TestClient
from main import app
import uuid

client = TestClient(app)


def test_create_base_lifecycle():

    kb_name = f"test_kb_{uuid.uuid4().hex}"

    # 创建知识库
    try:
        create_response = client.post(
            "/knowledge_bases",
            json={
                "name": kb_name,
                "description": "Test Knowledge Base",
            }
        )

        assert create_response.status_code == 200

        create_data = create_response.json()

        assert create_data["data"]["name"] == kb_name

        # 获取知识库信息

        get_response = client.get(
            f"/knowledge_bases/{kb_name}"
        )

        assert get_response.status_code == 200

        get_data = get_response.json()

        assert get_data["data"]["kb_name"] == kb_name

        # 获取所有知识库

        get_all_response = client.get("/knowledge_bases/all")

        assert get_all_response.status_code == 200

        all_data = get_all_response.json()

        names = [
            item["name"]
            for item in all_data["data"]
        ]

        assert kb_name in names

        # 删除知识库

        delete_response = client.delete(
            f"/knowledge_bases/{kb_name}"
        )

        assert delete_response.status_code == 200

        # 证明已删除

        verify_response = client.get(
            f"/knowledge_bases/{kb_name}"
        )

        assert verify_response.status_code == 404

    finally:
        # 确保清理
        client.delete(
            f"/knowledge_bases/{kb_name}"
        )
