from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

from app.core import pagination

@router.get("/search", response_model=pagination.Page[schemas.user.User])
def search_users(
    db: Session = Depends(deps.get_db),
    q: str = "",
    skip: int = 0,
    limit: int = 20,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Buscar usuarios por nombre o email.
    """
    users = crud.crud_user.search_users(db, query=q, skip=skip, limit=limit)
    total = crud.crud_user.count_search_users(db, query=q)
    page = (skip // limit) + 1
    return pagination.paginate(items=users, total=total, page=page, size=limit)

@router.get("/me", response_model=schemas.user.User)
def read_user_me(
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    return current_user

@router.put("/me", response_model=schemas.user.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserUpdate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    user = crud.crud_user.update_user(db, db_user=current_user, user_in=user_in)
    return user

from fastapi import UploadFile, File
from app.core import utils

@router.post("/me/image", response_model=schemas.user.User)
def upload_profile_image(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Subir imagen de perfil.
    """
    image_url = utils.save_upload_file(file, "uploads/profile_images")
    current_user.profile_image = image_url
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/{user_id}/follow")
def follow_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes seguirte a ti mismo")
    user_to_follow = db.query(models.user.User).filter(models.user.User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    crud.crud_user.follow_user(db, follower=current_user, to_follow=user_to_follow)
    
    # Notificación WebSocket e Historial
    import asyncio
    from app.core.notifications import manager
    
    msg = f"{current_user.full_name} ha empezado a seguirte"
    
    # Guardar en DB
    notification_in = schemas.notification.NotificationCreate(
        recipient_id=user_id,
        sender_id=current_user.id,
        type="follow",
        message=msg
    )
    crud.crud_notification.create_notification(db, notification=notification_in)
    
    # Enviar en tiempo real
    asyncio.create_task(manager.send_personal_message(
        {
            "type": "follow",
            "message": msg,
            "from_user_id": current_user.id
        },
        user_id=user_id
    ))
    
    return {"message": f"Ahora sigues a {user_to_follow.full_name}"}

@router.post("/{user_id}/unfollow")
def unfollow_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    user_to_unfollow = db.query(models.user.User).filter(models.user.User.id == user_id).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    crud.crud_user.unfollow_user(db, follower=current_user, to_unfollow=user_to_unfollow)
    return {"message": f"Has dejado de seguir a {user_to_unfollow.full_name}"}
