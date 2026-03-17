from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session
from app import crud, schemas
from app.api import deps
from app.core.config import settings
from app.core import security
from app.core.email import send_reset_password_email
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register", response_model=schemas.user.User)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserCreate
):
    user = crud.crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="El usuario con este email ya existe.",
        )
    return crud.crud_user.create_user(db, user=user_in)

from app.core import rate_limit

@router.post("/login/access-token", response_model=schemas.token.Token, dependencies=[Depends(rate_limit.rate_limit_login)])
def login_access_token(
    request: Request,
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Email o contraseña incorrectos")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    # Si 2FA está habilitado, devolver token temporal
    if user.is_two_factor_enabled:
        # Creamos un token corto para la verificación 2FA
        temp_token_expires = timedelta(minutes=5)
        temp_token, _, _ = security.create_access_token(
            user.id, expires_delta=temp_token_expires
        )
        return {
            "is_2fa_required": True,
            "temp_token_2fa": temp_token
        }
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token, jti, expires_at = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Registrar la sesión en la DB
    from app.models.session import UserSession
    db_session = UserSession(
        user_id=user.id,
        token_jti=jti,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host,
        expires_at=expires_at
    )
    db.add(db_session)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/login/2fa", response_model=schemas.token.Token)
def login_2fa(
    request: Request,
    verify_data: schemas.two_factor.TwoFactorVerify,
    db: Session = Depends(deps.get_db),
    # Usamos un dep especial o extraemos manualmente el sub del temp_token
    # Por simplicidad aquí lo extraeré del Authorization header (temp_token)
    token: str = Depends(deps.reusable_oauth2)
):
    from jose import jwt
    from pydantic import ValidationError
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = schemas.token.TokenPayload(**payload)
        user_id = token_data.sub
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=403, detail="Token temporal inválido")
        
    user = crud.crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    import pyotp
    totp = pyotp.TOTP(user.two_factor_secret)
    if not totp.verify(verify_data.token):
        raise HTTPException(status_code=400, detail="Código 2FA inválido")
        
    # Generar token real
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token, jti, expires_at = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Registrar la sesión en la DB
    from app.models.session import UserSession
    db_session = UserSession(
        user_id=user.id,
        token_jti=jti,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host,
        expires_at=expires_at
    )
    db.add(db_session)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/password-recovery/{email}", response_model=schemas.msg.Msg)
async def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Recuperación de contraseña por email.
    """
    user = crud.crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="El usuario con este email no existe en el sistema.",
        )
    password_reset_token = security.create_password_reset_token(email=email)
    await send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return {"msg": "Email de recuperación enviado"}

@router.post("/reset-password/", response_model=schemas.msg.Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Restablecer contraseña usando el token.
    """
    email = security.verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido")
    user = crud.crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="El usuario con este email no existe en el sistema.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Contraseña actualizada correctamente"}
