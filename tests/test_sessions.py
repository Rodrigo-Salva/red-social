import pytest
from fastapi.testclient import TestClient
from app.core.config import settings

def test_session_registration_on_login(client: TestClient):
    # 1. Registro
    user_data = {"email": "session_user@example.com", "password": "password123", "full_name": "Session User"}
    client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    
    # 2. Login
    login_data = {"username": "session_user@example.com", "password": "password123"}
    response = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # 3. Verificar sesión en DB
    response = client.get(
        f"{settings.API_V1_STR}/sessions/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) > 0
    assert sessions[0]["is_active"] is True

def test_session_revocation(client: TestClient):
    # 1. Login
    login_data = {"username": "session_user@example.com", "password": "password123"}
    response = client.post(f"{settings.API_V1_STR}/auth/login/access-token", data=login_data)
    token = response.json()["access_token"]
    
    # 3. Revocar sesión actual
    response = client.delete(
        f"{settings.API_V1_STR}/sessions/current",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # 4. Intentar usar el token de nuevo (debería fallar porque el jti fue revocado)
    response = client.get(
        f"{settings.API_V1_STR}/sessions/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "La sesión ha sido cerrada o es inválida"
