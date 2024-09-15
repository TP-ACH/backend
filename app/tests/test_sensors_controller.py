import pytest
import datetime
from fastapi.testclient import TestClient

from main import app
from clients.mongodb_client import mongo_client
from services.auth_service import get_current_user

def override_get_current_user():
    return {"username": "testuser", "email": "testuser@example.com", "password": "password123"}

@pytest.fixture(scope="module")
async def test_db():
    client = mongo_client
    db = client['test_db']

    await db["temperature"].insert_many([
        {"reading": 25.5, "created_at": datetime.datetime(2024, 9, 1, 12, 0)},
        {"reading": 26.3, "created_at": datetime.datetime(2024, 9, 2, 12, 0)},
        {"reading": 24.7, "created_at": datetime.datetime(2024, 9, 3, 12, 0)},
    ])

    await db["ph"].insert_many([
        {"reading": 7.0, "created_at": datetime.datetime(2024, 9, 1, 12, 0)},
        {"reading": 7.5, "created_at": datetime.datetime(2024, 9, 2, 12, 0)},
        {"reading": 6.8, "created_at": datetime.datetime(2024, 9, 3, 12, 0)},
    ])

    yield db

    client.drop_database('test_db')
    client.close()


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_device_data_temperature(client, test_db):
    response = client.get("/sensors/test_db?sensor=temperature&start_date=2024-09-01&end_date=2024-09-03")
    
    assert response.status_code == 200
    data = response.json()

    assert "temperature" in data
    assert data["temperature"]["max"] == 26.3
    assert data["temperature"]["min"] == 24.7
    assert len(data["temperature"]["data"]) == 3


def test_get_device_data_ph(client, test_db):
    response = client.get("/sensors/test_db?sensor=ph&start_date=2024-09-01&end_date=2024-09-03")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "ph" in data
    assert data["ph"]["max"] == 7.5
    assert data["ph"]["min"] == 6.8
    assert len(data["ph"]["data"]) == 3

def test_get_device_data_no_sensor_filter(client, test_db):
    response = client.get("/sensors/test_db?start_date=2024-09-01&end_date=2024-09-03")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "temperature" in data
    assert "ph" in data
    assert len(data["temperature"]["data"]) == 3
    assert len(data["ph"]["data"]) == 3

def test_get_device_data_date_filter(client, test_db):
    response = client.get("/sensors/test_db?sensor=temperature&start_date=2024-09-02&end_date=2024-09-03")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "temperature" in data
    assert len(data["temperature"]["data"]) == 2

def test_get_device_data_invalid_date(client, test_db):
    response = client.get("/sensors/test_db?sensor=temperature&start_date=2024-09-01&end_date=2024-09-33")
    
    assert response.status_code == 422

def test_get_device_data_start_date_only(client, test_db):
    response = client.get("/sensors/test_db?sensor=temperature&start_date=2024-09-02")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "temperature" in data
    assert len(data["temperature"]["data"]) == 2

def test_get_device_data_end_date_only(client, test_db):
    response = client.get("/sensors/test_db?sensor=temperature&end_date=2024-09-02")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "temperature" in data
    assert len(data["temperature"]["data"]) == 2

def test_get_device_data_invalid_device_id(client, test_db):
    response = client.get("/sensors/invalid_db?sensor=temperature&start_date=2024-09-01&end_date=2024-09-03")
    
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 0