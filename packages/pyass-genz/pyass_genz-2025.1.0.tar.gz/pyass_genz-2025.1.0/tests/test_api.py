# pyass🍑/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from pyass.api.rest import app

@pytest.fixture
def client():
    """Fixture: FastAPI test client"""
    return TestClient(app)

def test_api_health(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["slang_count"] > 0

def test_api_define(client):
    """Test define endpoint"""
    response = client.get("/define/rizz")
    assert response.status_code == 200
    data = response.json()
    assert data["term"].lower() == "rizz"
    assert "charisma" in data["definition"].lower()

def test_api_translate(client):
    """Test translate endpoint"""
    response = client.post("/translate", json={
        "text": "This is good",
        "intensity": 1.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == "This is good"
    assert "good" not in data["translated"].lower()
