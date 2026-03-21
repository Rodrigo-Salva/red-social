from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import schemas
import pytest

def test_poll_flow(client: TestClient, db_session: Session):
    # 1. Registro y login
    user_data = {"email": "polls@example.com", "password": "password", "full_name": "Polls User"}
    client.post("/api/v1/auth/register", json=user_data)
    login_data = {"username": "polls@example.com", "password": "password"}
    response = client.post("/api/v1/auth/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Crear un post
    post_data = {"title": "Post con Encuesta", "content": "¿Qué prefieres?"}
    response = client.post("/api/v1/posts/", headers=headers, data=post_data)
    post_id = response.json()["id"]

    # 3. Crear una encuesta para ese post
    poll_data = {
        "question": "¿Pizza o Sushi?",
        "options": ["Pizza 🍕", "Sushi 🍣"]
    }
    response = client.post(f"/api/v1/polls/posts/{post_id}/poll", headers=headers, json=poll_data)
    assert response.status_code == 200
    poll = response.json()
    poll_id = poll["id"]
    option_id = poll["options"][0]["id"]

    # 4. Votar
    response = client.post(f"/api/v1/polls/{poll_id}/vote", headers=headers, json={"option_id": option_id})
    assert response.status_code == 200

    # 5. Ver resultados
    response = client.get(f"/api/v1/polls/{poll_id}/results")
    assert response.status_code == 200
    results = response.json()
    assert results["options"][0]["votes_count"] == 1
    assert results["options"][1]["votes_count"] == 0

    # 6. Cambiar el voto
    other_option_id = poll["options"][1]["id"]
    client.post(f"/api/v1/polls/{poll_id}/vote", headers=headers, json={"option_id": other_option_id})
    response = client.get(f"/api/v1/polls/{poll_id}/results")
    assert response.status_code == 200
    results = response.json()
    assert results["options"][0]["votes_count"] == 0
    assert results["options"][1]["votes_count"] == 1
