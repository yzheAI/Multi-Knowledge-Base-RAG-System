from app.core.container import container
from app.config import KNOWLEDGE_BASE_PATH
from app.knowledge_base.manager import KnowledgeManager
import uuid
import os


def test_knowledge_base_lifecycle(
        client,
        auth_user,
        create_kb
):

    headers = auth_user["headers"]
    user_id = auth_user["user_id"]

    kb_name = create_kb()

    try:
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
