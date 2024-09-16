import pytest

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from main import app
from services.auth_service import get_password_hash


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def mock_mongo_client():
    with patch("clients.mongodb_client.mongo_client") as mock_client:
        mock_db = MagicMock()
        mock_users_collection = MagicMock()

        mock_client.get_database.return_value = mock_db
        mock_db.get_collection.return_value = mock_users_collection

        mock_users_collection.insert_one = AsyncMock()
        mock_users_collection.find_one = AsyncMock()

        yield mock_users_collection


def test_register(client, mock_mongo_client):
    mock_mongo_client.find_one.return_value = None

    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": "newpassword",
            "email": "newuser@example.com",
        },
    )
    assert response.status_code == 201
    mock_mongo_client.insert_one.assert_called_once()


def test_register_conflict(client, mock_mongo_client):
    mock_mongo_client.find_one.return_value = {
        "username": "existinguser",
        "password": get_password_hash("password123"),
    }

    response = client.post(
        "/auth/register",
        json={
            "username": "existinguser",
            "password": "password123",
            "email": "existinguser@example.com",
        },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Username already registered"}


def test_register_missing_required_fields(client, mock_mongo_client):
    mock_mongo_client.find_one.return_value = None

    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
        },
    )
    assert response.status_code == 422


def test_login(client, mock_mongo_client):
    mock_mongo_client.find_one.return_value = {
        "username": "testuser",
        "password": get_password_hash("testpassword"),
    }

    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_credentials(client, mock_mongo_client):
    mock_mongo_client.find_one.return_value = {
        "username": "testuser",
        "password": get_password_hash("testpassword"),
    }

    response = client.post(
        "/auth/login", data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}
