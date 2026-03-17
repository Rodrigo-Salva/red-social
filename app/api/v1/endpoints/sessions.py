from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.session.UserSession])
def read_active_sessions(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Listar todas las sesiones activas del usuario actual.
    """
    return [s for s in current_user.sessions if s.is_active]

@router.delete("/current", response_model=schemas.msg.Msg)
def logout_current_session(
    db: Session = Depends(deps.get_db),
    token: str = Depends(deps.reusable_oauth2),
) -> Any:
    """
    Cerrar la sesión actual (logout).
    """
    try:
        from jose import jwt
        from app.core.config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
    except Exception:
        raise HTTPException(status_code=403, detail="Token inválido")
    
    session = db.query(models.session.UserSession).filter(
        models.session.UserSession.token_jti == jti
    ).first()
    
    if session:
        session.is_active = False
        db.add(session)
        db.commit()
        
    return {"msg": "Sesión cerrada correctamente"}

@router.delete("/{session_id}", response_model=schemas.msg.Msg)
def revoke_session(
    session_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Cerrar una sesión específica.
    """
    print(f"DEBUG: Revoking session {session_id} for user {current_user.id}")
    session = db.query(models.session.UserSession).filter(
        models.session.UserSession.id == session_id,
        models.session.UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    session.is_active = False
    db.add(session)
    db.commit()
    db.refresh(session)
    print(f"DEBUG: Session {session.id} is_active after commit/refresh: {session.is_active}")
    return {"msg": "Sesión cerrada correctamente"}
