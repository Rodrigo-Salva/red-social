from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.notification.Notification])
def read_notifications(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """
    Obtener notificaciones del usuario actual.
    """
    notifications = crud.crud_notification.get_user_notifications(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return notifications

@router.put("/{id}/read", response_model=schemas.notification.Notification)
def mark_notification_read(
    id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Marcar notificación como leída.
    """
    notification = crud.crud_notification.mark_as_read(db, notification_id=id)
    return notification
