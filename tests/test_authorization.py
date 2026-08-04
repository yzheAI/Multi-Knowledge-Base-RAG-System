import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_user_and_login():
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
    data = login.json()
    return {
        "Authorization": f"Bearer {data['access_token']}",
    }


def create_knowledge_base(headers):
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


def test_user_cannot_access_other_users_knowledge_base():
    # 用户A
    user_a_headers = create_user_and_login()
    # 用户B
    user_b_headers = create_user_and_login()

    kb_name = create_knowledge_base(user_a_headers)

    response = client.get(
        f"/knowledge_bases/{kb_name}",
        headers=user_b_headers
    )

    assert response.status_code == 404


def test_user_cannot_delete_other_users_knowledge_base():
    # 用户A
    user_a_headers = create_user_and_login()
    # 用户B
    user_b_headers = create_user_and_login()

    kb_name = create_knowledge_base(user_a_headers)

    response = client.delete(
        f"/knowledge_bases/{kb_name}",
        headers=user_b_headers
    )

    assert response.status_code == 404


def test_user_cannot_upload_to_other_users_knowledge_base():
    # 用户A
    user_a_headers = create_user_and_login()
    # 用户B
    user_b_headers = create_user_and_login()

    kb_name = create_knowledge_base(user_a_headers)

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
