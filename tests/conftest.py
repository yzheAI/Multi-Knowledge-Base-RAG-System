import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.cache.retrieval_cache import RetrievalCache
from app.database.session import Base
import uuid
from main import app
from app.database.session import get_db
from fastapi.testclient import TestClient
import os

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(
    TEST_DATABASE_URL
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# 覆盖FastAPI dependency
@pytest.fixture(scope='session', autouse=True)
def create_tables():
    """
    会话执行一次，所有测试用例共享
    自动调用
    """
    Base.metadata.create_all(
        test_engine
    )

    yield  # 暂停交于测试用例

    Base.metadata.drop_all(
        test_engine
    )  # 删除所有表


@pytest.fixture(scope="session", autouse=True)
def override_database():

    def override_get_db():

        db = TestSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()


# 专门提供给test_xxx
@pytest.fixture
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    client = TestClient(app)
    return client


@pytest.fixture
def auth_user(client):
    username = f"test_{uuid.uuid4().hex}"
    password = "123456"

    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
        }
    )

    login = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        }
    )

    token = login.json()["access_token"]

    data = login.json()

    return {
        "headers": {
            "Authorization": f"Bearer {token}",
        },
        "user_id": data["user_id"]
    }


@pytest.fixture
def auth_user_2(client):
    username = f"test_{uuid.uuid4().hex}"
    password = "123456"

    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password,
        }
    )

    login = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        }
    )

    token = login.json()["access_token"]

    data = login.json()

    return {
        "headers": {
            "Authorization": f"Bearer {token}",
        },
        "user_id": data["user_id"]
    }


@pytest.fixture
def create_kb(client, auth_user):

    def _create_kb():

        kb_name = f"test_kb_{uuid.uuid4().hex}"

        response = client.post(
            "/knowledge_bases",
            headers=auth_user["headers"],
            json={
                "name": kb_name,
                "description": "test",
            }
        )

        assert response.status_code == 200

        return kb_name

    return _create_kb


@pytest.fixture
def retrieval_kb(client, auth_user, create_kb):
    kb_name = create_kb()

    file = {
        "file": (
            "retrieval.txt",
            """
            铜基复合材料是一种由铜基体和增强相组成的复合材料。
            常见制备方法包括粉末冶金法、搅拌铸造法。
            铜基复合材料具有良好的导电性和力学性能。
            """,
            "text/plain"
        )
    }

    response = client.post(
        "/files/",
        headers=auth_user["headers"],
        files=file,
        data={
            "kb_name": kb_name
        }
    )

    assert response.status_code == 200

    return kb_name


@pytest.fixture
def retrieval_cache():
    cache = RetrievalCache()

    yield cache

    cache.delete_by_kb(
        1,
        10
    )
