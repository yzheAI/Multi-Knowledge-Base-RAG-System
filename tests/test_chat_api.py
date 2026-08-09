def test_chat_api(
        client,
        auth_user,
        retrieval_kb
):
    response = client.post(
        "/chat/chat/stream",
        json={
            "query": "铜基复合材料是什么？",
            "kb_name": retrieval_kb
        },
        headers=auth_user["headers"]
    )

    assert response.headers["content-type"].startswith(
        "text/event-stream"
    )

    content = response.text

    assert len(content) > 0

    assert "铜基复合材料" in content
