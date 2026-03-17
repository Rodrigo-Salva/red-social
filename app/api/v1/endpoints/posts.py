from typing import Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Form
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.post.Post])
def read_posts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    only_images: bool = False,
    sort_by_popularity: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Any:
    """
    Recuperar publicaciones con filtros avanzados.
    """
    posts = crud.crud_post.get_posts(
        db, 
        skip=skip, 
        limit=limit, 
        only_images=only_images,
        sort_by_popularity=sort_by_popularity,
        start_date=start_date,
        end_date=end_date
    )
    return posts

@router.get("/search", response_model=List[schemas.post.Post])
def search_posts(
    q: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Buscar publicaciones por título o contenido.
    """
    posts = db.query(models.user.Post).filter(
        (models.user.Post.title.ilike(f"%{q}%")) |
        (models.user.Post.content.ilike(f"%{q}%"))
    ).limit(10).all()
    return posts

from app.core import pagination

@router.get("/feed", response_model=pagination.Page[schemas.post.Post])
def read_feed(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """
    Obtener feed de noticias personalizado.
    """
    posts = crud.crud_post.get_feed(db, user=current_user, skip=skip, limit=limit)
    total = crud.crud_post.get_feed_count(db, user=current_user)
    page = (skip // limit) + 1
    return pagination.paginate(items=posts, total=total, page=page, size=limit)

from fastapi import UploadFile, File, Form
from app.core import utils

@router.post("/", response_model=schemas.post.Post)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    title: str = Form(...),
    content: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear nueva publicación con imagen opcional.
    """
    image_url = None
    if file:
        image_url = utils.save_upload_file(file, "uploads/post_images")
    
    post_in = schemas.post.PostCreate(title=title, content=content, image_url=image_url)
    post = crud.crud_post.create_user_post(db=db, post=post_in, owner_id=current_user.id)
    return post

@router.delete("/{id}", response_model=schemas.post.Post)
def delete_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Eliminar una publicación.
    """
    post = crud.crud_post.get_post(db=db, post_id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="No tienes permisos suficientes")
    post = crud.crud_post.delete_post(db=db, post_id=id)
    return post

@router.post("/{id}/like", response_model=schemas.post.Post)
def like_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Dar like a una publicación.
    """
    post = crud.crud_post.get_post(db=db, post_id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    post = crud.crud_post.like_post(db, user=current_user, post=post)
    
    # Notificación WebSocket e Historial
    import asyncio
    from app.core.notifications import manager
    if post.owner_id != current_user.id:
        msg = f"A {current_user.full_name} le gusta tu publicación"
        
        # Guardar en DB
        notification_in = schemas.notification.NotificationCreate(
            recipient_id=post.owner_id,
            sender_id=current_user.id,
            type="like",
            message=msg,
            post_id=post.id
        )
        crud.crud_notification.create_notification(db, notification=notification_in)
        
        # Enviar tiempo real
        asyncio.create_task(manager.send_personal_message(
            {
                "type": "like",
                "message": msg,
                "post_id": post.id
            },
            user_id=post.owner_id
        ))
    
    return post

@router.post("/{id}/unlike", response_model=schemas.post.Post)
def unlike_post(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Quitar like a una publicación.
    """
    post = crud.crud_post.get_post(db=db, post_id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    post = crud.crud_post.unlike_post(db, user=current_user, post=post)
    return post

@router.post("/{id}/comments", response_model=schemas.post.Comment)
def create_comment(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    comment_in: schemas.post.CommentBase,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Comentar en una publicación.
    """
    post = crud.crud_post.get_post(db=db, post_id=id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    
    comment_create = schemas.post.CommentCreate(content=comment_in.content, post_id=id)
    comment = crud.crud_comment.create_comment(db=db, comment=comment_create, owner_id=current_user.id)
    
    # Notificación WebSocket e Historial
    import asyncio
    from app.core.notifications import manager
    if post.owner_id != current_user.id:
        msg = f"{current_user.full_name} comentó tu publicación"
        
        # Guardar en DB
        notification_in = schemas.notification.NotificationCreate(
            recipient_id=post.owner_id,
            sender_id=current_user.id,
            type="comment",
            message=msg,
            post_id=post.id
        )
        crud.crud_notification.create_notification(db, notification=notification_in)
        
        # Enviar tiempo real
        asyncio.create_task(manager.send_personal_message(
            {
                "type": "comment",
                "message": msg,
                "post_id": post.id,
                "comment_id": comment.id
            },
            user_id=post.owner_id
        ))
        
    return comment
