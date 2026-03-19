from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core import utils
from app.crud import crud_story

router = APIRouter()

@router.post("/", response_model=schemas.story.Story)
def create_story(
    *,
    db: Session = Depends(deps.get_db),
    content: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear una nueva historia (expira en 24h).
    """
    media = utils.save_upload_file(file, "uploads/stories")
    story_in = schemas.story.StoryCreate(content=content, image_url=media["image_url"])
    story = crud_story.create_story(db=db, story=story_in, owner_id=current_user.id)
    return story

@router.get("/feed", response_model=List[schemas.story.Story])
def read_stories_feed(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener historias activas de los usuarios que sigues.
    """
    return crud_story.get_active_stories_for_user_feed(db, user=current_user)

@router.get("/me", response_model=List[schemas.story.Story])
def read_my_stories(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Obtener mis propias historias activas.
    """
    return crud_story.get_user_stories(db, user_id=current_user.id)

@router.delete("/{id}", response_model=schemas.story.Story)
def delete_story(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Eliminar una historia propia.
    """
    story = db.query(models.story.Story).filter(models.story.Story.id == id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    if story.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="No tienes permisos suficientes")
    return crud_story.delete_story(db=db, story_id=id)
