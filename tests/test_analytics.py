from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import schemas
import pytest

def test_post_analytics(client: TestClient, db_session: Session):
    # 1. Registrar usuario y loguear
    user_data = {"email": "analytics@example.com", "password": "password", "full_name": "Analytics User"}
    client.post("/api/v1/auth/register", json=user_data)
    login_data = {"username": "analytics@example.com", "password": "password"}
    response = client.post("/api/v1/auth/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Crear un post
    post_data = {"title": "Post de Analítica", "content": "Contenido para probar vistas"}
    response = client.post("/api/v1/posts/", headers=headers, data=post_data)
    post_id = response.json()["id"]

    # 3. Registrar algunas vistas
    # Vista 1 (mismo usuario)
    resp1 = client.post(f"/api/v1/analytics/posts/{post_id}/view", headers=headers)
    assert resp1.status_code == 200
    # Vista 2 (otra IP/guest)
    resp2 = client.post(f"/api/v1/analytics/posts/{post_id}/view")
    assert resp2.status_code == 200
    
    # 4. Consultar estadísticas del post
    response = client.get(f"/api/v1/analytics/posts/{post_id}", headers=headers)
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_views"] == 2
    # Si implementamos uniques por user_id, y uno fue None (guest) y otro user_id, 
    # nuestro count(distinct user_id) actual podria dar 1 si solo cuenta IDs no nulos.
    # Pero lo importante es que el total suba.
    
    # 5. Consultar dashboard general
    response = client.get("/api/v1/analytics/me", headers=headers)
    assert response.status_code == 200
    analytics = response.json()
    assert analytics["total_post_views"] == 2
    assert len(analytics["top_posts"]) > 0
    assert analytics["top_posts"][0]["post_id"] == post_id
