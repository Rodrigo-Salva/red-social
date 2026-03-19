from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.crud import crud_analytics

router = APIRouter()

@router.get("/me", response_model=schemas.analytics.UserAnalytics)
def read_my_analytics(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener estadísticas detalladas del perfil del usuario actual.
    """
    return crud_analytics.get_user_analytics(db, user_id=current_user.id)

@router.get("/posts/{post_id}", response_model=schemas.analytics.PostStats)
def read_post_stats(
    post_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener estadísticas de una publicación específica (solo si eres el dueño).
    """
    post = crud.crud_post.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver estas estadísticas")
    return crud_analytics.get_post_stats(db, post_id=post_id)

@router.post("/posts/{post_id}/view")
def record_post_view(
    post_id: int,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user_optional: Optional[models.user.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Registrar una visualización de un post.
    """
    post = crud.crud_post.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    
    user_id = current_user_optional.id if current_user_optional else None
    ip_address = request.client.host
    
    crud_analytics.create_post_view(db, post_id=post_id, user_id=user_id, ip_address=ip_address)
    return {"status": "ok"}
