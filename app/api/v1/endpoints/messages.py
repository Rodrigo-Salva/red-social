from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.message.Message)
def send_message(
    *,
    db: Session = Depends(deps.get_db),
    message_in: schemas.message.MessageCreate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Enviar un mensaje privado a otro usuario.
    """
    if current_user.id == message_in.recipient_id:
        raise HTTPException(
            status_code=400, detail="No puedes enviarte un mensaje a ti mismo"
        )
    
    recipient = db.query(models.user.User).filter(
        models.user.User.id == message_in.recipient_id,
        models.user.User.is_deleted == False
    ).first()
    
    if not recipient:
        raise HTTPException(status_code=404, detail="Destinatario no encontrado")
        
    message = crud.crud_message.create_message(
        db, message=message_in, sender_id=current_user.id
    )
    
    # Notificación WebSocket opcional para tiempo real de DMs
    from app.core.notifications import manager
    import asyncio
    asyncio.create_task(manager.send_personal_message(
        {
            "type": "new_message",
            "from_id": current_user.id,
            "message": message.content
        },
        user_id=message_in.recipient_id
    ))
    
    return message

@router.get("/{other_user_id}", response_model=List[schemas.message.Message])
def get_chat(
    other_user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """
    Obtener la conversación con un usuario específico.
    """
    crud.crud_message.mark_as_read(db, user_id=current_user.id, sender_id=other_user_id)
    messages = crud.crud_message.get_messages(
        db, user_id=current_user.id, other_user_id=other_user_id, skip=skip, limit=limit
    )
    return messages

@router.get("/conversations/list", response_model=List[schemas.message.Message])
def list_conversations(
    db: Session = Depends(deps.get_db),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Listar todas las conversaciones del usuario (resumen).
    """
    return crud.crud_message.get_conversations(db, user_id=current_user.id)
