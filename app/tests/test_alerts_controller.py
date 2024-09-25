import pytest
import datetime
from fastapi.testclient import TestClient

from main import app
from clients.mongodb_client import mongo_client
from services.auth_service import get_current_user
from utils.alerts import Status, Topic, Type


def override_get_current_user():
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
    }

@pytest.fixture(scope="module")
async def test_db():
    client = mongo_client
    db = client["test_db"]

    await db["alerts"].insert_many(
        [
            {"device_id": "123", "type": "ok", "status": "open", "topic": "ph_ok"},
            {"device_id": "123", "type": "error", "status": "open", "topic": "connection_lost"},
            {"device_id": "123", "type": "warning", "status": "open", "topic": "ph_up"},
            {"device_id": "1234", "type": "ok", "status": "open", "topic": "ec_ok"},
            {"device_id": "1234", "type": "error", "status": "open", "topic": "ph_fail"},
        ]
    )

    yield db

    client.drop_database("test_db")
    client.close()


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

def test_get_alerts_no_filter(client):
    response = client.get("/alerts")

    assert response.status_code == 200
    data = response.json()
    print(data)

    assert len(data) == 5
    assert data[0]["device_id"] == "123"
    assert data[0]["type"] == "ok"
    assert data[0]["status"] == "open"
    assert data[0]["topic"] == "ph_ok"
    assert data[0]["message"] == "Se estabilizó el pH"
    
def test_get_alerts_with_device_id_filter(client, test_db):
    response = client.get("/alerts/?device_id=123")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
def test_get_alerts_with_status_filter(client, test_db):
    response = client.get(f"/alerts/?status={Status.OPEN.value}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    
    response = client.get(f"/alerts/?status={Status.CLOSED.value}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    
def test_get_alerts_with_topic_filter(client, test_db):
    response = client.get(f"/alerts/?topic={Topic.CONNECTION_LOST.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["device_id"] == "123"
    assert data[0]["topic"] == "connection_lost"
    
def test_create_new_alert(client, test_db):
    new_alert = {
        "_id": "test",
        "device_id": "999",
        "type": "warning",
        "status": "open",
        "topic": "ph_up"
    }
    response = client.post("/alerts", json=new_alert)    
    assert response.status_code == 200
    data = response.json()
    alert_id = data["_id"]
    assert alert_id != "test"
    assert data["device_id"] == "999"
    assert data["topic"] == "ph_up"
    
    get_response = client.get(f"/alerts/?device_id=999&type=warning&status=open&topic=ph_up")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data) == 1
    assert data["_id"] == alert_id
    
def test_create_existing_alert_wont_create(client, test_db):
    new_alert = {
        "_id": "test",
        "device_id": "123",
        "type": "ok",
        "status": "pending",
        "topic": "ph_ok",
    }
    response = client.post("/alerts/", json=new_alert)
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == "123"
    assert data["topic"] == "ph_ok"
    assert data["status"] == "open"

    get_response = client.get(f"/alerts/?device_id=123&type=ok&status=open&topic=ph_ok")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert len(get_data) == 1
    
def test_update_alert(client, test_db):
    response = client.get(f"/alerts/?device_id=999")
    data = response.json()
    alert_id = data[0]["_id"]
    
    response = client.put(f"/alerts/?id={alert_id}&status={Status.CLOSED.value}")
    assert response.status_code == 204
    data = response.json()

    response = client.get(f"/alerts/?status={Status.CLOSED.value}")
    data = response.json()
    assert len(data) == 1
    assert data[0]["_id"] == alert_id
    assert data[0]["status"] == "closed"
    
def test_delete_alert(client, test_db):
    response = client.get(f"/alerts/?device_id=999")
    data = response.json()
    alert_id = data[0]["_id"]

    response = client.delete(f"/alerts/?id={alert_id}")
    assert response.status_code == 204

    response = client.get(f"/alerts/?device_id=999")
    data = response.json()
    assert len(data) == 0