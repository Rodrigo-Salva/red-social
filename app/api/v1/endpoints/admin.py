from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/users", response_model=List[schemas.user.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.user.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Listar todos los usuarios del sistema (Solo Admin).
    """
    users = crud.crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/stats")
def get_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Obtener estadísticas globales (Solo Admin).
    """
    return {
        "users_count": db.query(models.user.User).count(),
        "posts_count": db.query(models.post.Post).count(),
    }
