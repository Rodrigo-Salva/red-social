from typing import Any
import pyotp
import qrcode
import io
import base64
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()

@router.post("/setup", response_model=schemas.two_factor.TwoFactorSetupResponse)
def setup_2fa(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Generar secreto 2FA y URI para QR.
    """
    if current_user.is_two_factor_enabled:
        raise HTTPException(
            status_code=400,
            detail="La autenticación de dos factores ya está activada"
        )
    
    # Generar secreto si no existe
    if not current_user.two_factor_secret:
        secret = pyotp.random_base32()
        current_user.two_factor_secret = secret
        db.add(current_user)
        db.commit()
    else:
        secret = current_user.two_factor_secret
        
    otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name=settings.PROJECT_NAME
    )
    
    # Generar QR Code en base64
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(otpauth_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "secret": secret,
        "otpauth_url": otpauth_url,
        "qr_code_base64": f"data:image/png;base64,{img_str}"
    }

@router.post("/enable", response_model=schemas.msg.Msg)
def enable_2fa(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
    verify_data: schemas.two_factor.TwoFactorVerify
) -> Any:
    """
    Verificar el primer código y activar 2FA.
    """
    if current_user.is_two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA ya está activo")
        
    if not current_user.two_factor_secret:
        raise HTTPException(status_code=400, detail="Debe configurar 2FA primero")
        
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(verify_data.token):
        raise HTTPException(status_code=400, detail="Código de verificación inválido")
        
    current_user.is_two_factor_enabled = True
    db.add(current_user)
    db.commit()
    
    return {"msg": "Autenticación de dos factores activada correctamente"}

@router.post("/disable", response_model=schemas.msg.Msg)
def disable_2fa(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
    verify_data: schemas.two_factor.TwoFactorVerify
) -> Any:
    """
    Desactivar 2FA.
    """
    if not current_user.is_two_factor_enabled:
        raise HTTPException(status_code=400, detail="2FA no está activo")
        
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(verify_data.token):
        raise HTTPException(status_code=400, detail="Código de verificación inválido")
        
    current_user.is_two_factor_enabled = False
    current_user.two_factor_secret = None
    db.add(current_user)
    db.commit()
    
    return {"msg": "Autenticación de dos factores desactivada correctamente"}
