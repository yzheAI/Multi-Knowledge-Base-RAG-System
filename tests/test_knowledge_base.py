def test_knowledge_base_lifecycle(
        client,
        auth_user,
        create_kb
):

    headers = auth_user["headers"]

    kb_name = create_kb()

    try:
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
        verify_response = client.get(
            f"/knowledge_bases/{kb_name}",
            headers=headers
        )

        assert verify_response.status_code == 404

    finally:
        # 确保清理
        try:
            client.delete(
                f"/knowledge_bases/{kb_name}",
                headers=headers
            )
        except Exception:
            pass
