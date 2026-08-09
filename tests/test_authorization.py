import uuid


def create_knowledge_base(
        client,
        headers
):
    kb_name = f"test_{uuid.uuid4().hex}"

    response = client.post(
        "/knowledge_bases",
        headers=headers,
        json={
            "name": kb_name,
            "description": "authorization test",
        }
    )

    assert response.status_code == 200

    return kb_name


def test_user_cannot_access_other_users_knowledge_base(
        client,
        auth_user,
        auth_user_2
):
    # 用户A
    user_a_headers = auth_user["headers"]
    # 用户B
    user_b_headers = auth_user_2["headers"]

    kb_name = create_knowledge_base(client, user_a_headers)

    response = client.get(
        f"/knowledge_bases/{kb_name}",
        headers=user_b_headers
    )

    assert response.status_code == 404


def test_user_cannot_delete_other_users_knowledge_base(
        client,
        auth_user,
        auth_user_2
):
    # 用户A
    user_a_headers = auth_user["headers"]
    # 用户B
    user_b_headers = auth_user_2["headers"]

    kb_name = create_knowledge_base(client, user_a_headers)

    response = client.delete(
        f"/knowledge_bases/{kb_name}",
        headers=user_b_headers
    )

    assert response.status_code == 404


def test_user_cannot_upload_to_other_users_knowledge_base(
        client,
        auth_user,
        auth_user_2
):
    # 用户A
    user_a_headers = auth_user["headers"]
    # 用户B
    user_b_headers = auth_user_2["headers"]

    kb_name = create_knowledge_base(client, user_a_headers)

    file = {
        "file": (
            "test.txt",
            "secret content",
            "text/plain"
        )
    }

    data = {
        "kb_name": kb_name
    }

    response = client.post(
        "/files",
        headers=user_b_headers,
        files=file,
        data=data
    )

    assert response.status_code == 404
