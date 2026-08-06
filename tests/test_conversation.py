def test_conversation(
        client,
        auth_user,
        create_kb
):
    kb_name = create_kb()

    response = client.post(
        '/chat/create_conversation',
        params={
            "kb_name": kb_name
        },
        headers=auth_user["headers"]
    )

    assert response.status_code == 200

    conversation_data = response.json()

    assert "conversation_id" in conversation_data

    result = client.get(
        '/chat/conversations',
        params={
            "kb_name": kb_name,
        },
        headers=auth_user["headers"]
    )

    assert result.status_code == 200

    conversations = result.json()

    assert isinstance(
        conversations,
        list
    )

    conversation_id = conversation_data["conversation_id"]

    res = client.get(
        f"/chat/messages/{conversation_id}",
        headers=auth_user["headers"]
    )

    assert res.status_code == 200

    messages = res.json()

    assert isinstance(
        messages,
        list
    )

    delete = client.delete(
        f"/chat/conversation/{conversation_id}",
        headers=auth_user["headers"]
    )

    assert delete.status_code == 200

    res = client.get(
        f"/chat/messages/{conversation_id}",
        headers=auth_user["headers"]
    )

    assert res.status_code == 404
