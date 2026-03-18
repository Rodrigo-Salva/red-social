from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/{user_id}", response_model=schemas.block.Block)
def block_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Bloquear a un usuario.
    """
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes bloquearte a ti mismo")
    
    user_to_block = crud.get(db, id=user_id)
    if not user_to_block:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if crud.crud_block.is_blocked(db, blocker_id=current_user.id, blocked_id=user_id):
        raise HTTPException(status_code=400, detail="El usuario ya está bloqueado")
    
    # Eliminar relación de seguimiento si existe
    crud.unfollow_user(db, follower=current_user, to_unfollow=user_to_block)
    crud.unfollow_user(db, follower=user_to_block, to_unfollow=current_user)
    
    return crud.crud_block.block_user(db, blocker_id=current_user.id, blocked_id=user_id)

@router.delete("/{user_id}", response_model=schemas.block.Block)
def unblock_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Desbloquear a un usuario.
    """
    block = crud.crud_block.unblock_user(db, blocker_id=current_user.id, blocked_id=user_id)
    if not block:
        raise HTTPException(status_code=404, detail="Bloqueo no encontrado")
    return block

@router.get("/", response_model=List[schemas.block.Block])
def get_blocks(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Listar usuarios bloqueados.
    """
    return crud.crud_block.get_blocked_users(db, user_id=current_user.id)
