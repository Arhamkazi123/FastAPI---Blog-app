import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import User, Post, Comment  # noqa: F401


# --- 1. In-memory test database with StaticPool ---
# StaticPool makes sure all connections share the same in-memory database.
# Without it, different connections would get different empty databases.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# --- 2. Fixture: test client with fresh tables for every test ---
@pytest.fixture(name="client")
def client_fixture():
    # Create all tables on the test database
    SQLModel.metadata.create_all(test_engine)

    # Override get_session so routes use test database
    def get_test_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session

    client = TestClient(app)
    yield client

    # Cleanup: drop tables and remove override
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(test_engine)


# --- 3. Fixture: a pre-made logged-in user ---
@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpass123",
    })

    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
