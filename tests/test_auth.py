import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_success():
    username = f"user_{uuid.uuid4().hex}"
    response = client.post(
        "/auth/register",
        json={
            "username": username,
            "password": "123456",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username


def test_register_duplicate():
    username = f"user_{uuid.uuid4().hex}"
    payload = {
        "username": username,
        "password": "123456"
    }

    first_register = client.post(
        "/auth/register",
        json=payload
    )

    assert first_register.status_code == 200

    second_register = client.post(
        "/auth/register",
        json=payload
    )

    assert second_register.status_code == 409


def test_login_success():
    username = f"user_{uuid.uuid4().hex}"
    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "123456"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data


def test_login_wrong_password():
    username = f"user_{uuid.uuid4().hex}"
    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": "123456"
        }
    )
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "12345"
        }
    )
    assert response.status_code == 401


def test_access_without_token():
    response = client.get(
        "/knowledge_bases/all"
    )
    assert response.status_code == 401
