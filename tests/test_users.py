import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_create_user(client: TestClient):
    data = {"email": "testuser@example.com", "password": "password123", "full_name": "Test User"}
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == data["email"]
    assert "id" in content

def test_login_user(client: TestClient):
    # Primero nos aseguramos de que el usuario existe
    login_data = {
        "username": "testuser@example.com",
        "password": "password123",
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    assert response.status_code == 200
    content = response.json()
    assert "access_token" in content
    assert content["token_type"] == "bearer"
