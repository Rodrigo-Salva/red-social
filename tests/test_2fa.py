import pyotp
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings

def test_2fa_full_flow(client: TestClient, db_session: Session):
    # 1. Registro y Login Normal
    user_email = "2fa_user@example.com"
    user_password = "password123"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"email": user_email, "password": user_password, "full_name": "2FA User"}
    )
    
    login_res = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={"username": user_email, "password": user_password}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Setup 2FA
    setup_res = client.post(
        f"{settings.API_V1_STR}/auth/2fa/setup",
        headers=headers
    )
    assert setup_res.status_code == 200
    secret = setup_res.json()["secret"]
    
    # 3. Activar 2FA con un código válido
    totp = pyotp.TOTP(secret)
    verify_token = totp.now()
    
    enable_res = client.post(
        f"{settings.API_V1_STR}/auth/2fa/enable",
        headers=headers,
        json={"token": verify_token}
    )
    assert enable_res.status_code == 200
    
    # 4. Intentar login normal (debería pedir 2FA)
    login_2fa_req = client.post(
        f"{settings.API_V1_STR}/auth/login/access-token",
        data={"username": user_email, "password": user_password}
    )
    assert login_2fa_req.status_code == 200
    res_data = login_2fa_req.json()
    assert res_data["is_2fa_required"] is True
    temp_token = res_data["temp_token_2fa"]
    
    # 5. Completar login con 2FA
    verify_token_2 = totp.now()
    final_login_res = client.post(
        f"{settings.API_V1_STR}/auth/login/2fa",
        headers={"Authorization": f"Bearer {temp_token}"},
        json={"token": verify_token_2}
    )
    assert final_login_res.status_code == 200
    assert "access_token" in final_login_res.json()
    
    # 6. Desactivar 2FA
    final_token = final_login_res.json()["access_token"]
    disable_res = client.post(
        f"{settings.API_V1_STR}/auth/2fa/disable",
        headers={"Authorization": f"Bearer {final_token}"},
        json={"token": totp.now()}
    )
    assert disable_res.status_code == 200
