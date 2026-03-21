from datetime import datetime
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.crud import crud_poll

router = APIRouter()

@router.post("/posts/{post_id}/poll", response_model=schemas.poll.Poll)
def create_post_poll(
    post_id: int,
    poll_in: schemas.poll.PollCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Crear una encuesta asociada a un post. Solo el dueño del post puede hacerlo.
    """
    post = crud.crud_post.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el dueño del post puede añadir encuestas")
    
    # Verificar si ya tiene encuesta
    if hasattr(post, 'poll') and post.poll:
        raise HTTPException(status_code=400, detail="Este post ya tiene una encuesta")
    
    return crud_poll.create_poll(db, post_id=post_id, poll_in=poll_in)

@router.post("/{poll_id}/vote")
def vote_in_poll(
    poll_id: int,
    vote_in: schemas.poll.PollVoteCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Votar en una encuesta.
    """
    poll = db.query(models.poll.Poll).filter(models.poll.Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    
    # Verificar si ha expirado
    if poll.expires_at and poll.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Esta encuesta ya ha expirado")
        
    success = crud_poll.vote_in_poll(
        db, poll_id=poll_id, user_id=current_user.id, option_id=vote_in.option_id
    )
    if not success:
         raise HTTPException(status_code=400, detail="No se pudo registrar el voto")
         
    return {"status": "ok"}

@router.get("/{poll_id}/results", response_model=schemas.poll.Poll)
def get_poll_results(
    poll_id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Obtener los resultados actuales de una encuesta.
    """
    poll = crud_poll.get_poll_results(db, poll_id=poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="Encuesta no encontrada")
    return poll
