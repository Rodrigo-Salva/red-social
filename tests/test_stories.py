from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.core import security
from app import schemas
import pytest
from io import BytesIO

def test_create_and_read_stories(client: TestClient, db_session: Session):
    # Crear usuario de prueba
    user_data = {"email": "story@example.com", "password": "password", "full_name": "Story User"}
    client.post("/api/v1/auth/register", json=user_data)
    login_data = {"username": "story@example.com", "password": "password"}
    response = client.post("/api/v1/auth/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Crear historia con imagen real (1x1)
    from PIL import Image
    file = BytesIO()
    image = Image.new('RGB', (1, 1))
    image.save(file, 'JPEG')
    file.seek(0)
    file.name = "test_story.jpg"
    
    response = client.post(
        "/api/v1/stories/",
        headers=headers,
        data={"content": "Mi primera historia"},
        files={"file": ("test_story.jpg", file, "image/jpeg")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Mi primera historia"
    assert "image_url" in data
    assert "webp" in data["image_url"]
    
    # Leer historias (me)
    response = client.get("/api/v1/stories/me", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    
    # Leer feed (debe estar vacio si no sigo a nadie mas, pero debe incluir la mia si asi se diseñó)
    # En nuestro crud_story, incluimos la propia en el feed
    response = client.get("/api/v1/stories/feed", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
