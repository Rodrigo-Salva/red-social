from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.message import Message
from app.schemas.message import MessageCreate

def create_message(db: Session, message: MessageCreate, sender_id: int):
    db_message = Message(
        sender_id=sender_id,
        recipient_id=message.recipient_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_messages(db: Session, user_id: int, other_user_id: int, skip: int = 0, limit: int = 50):
    return db.query(Message).filter(
        or_(
            (Message.sender_id == user_id) & (Message.recipient_id == other_user_id),
            (Message.sender_id == other_user_id) & (Message.recipient_id == user_id)
        )
    ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()

def get_conversations(db: Session, user_id: int):
    # En una red social real, esto sería más complejo para obtener el último mensaje de cada chat
    # Aquí simplificamos retornando todos los mensajes donde el usuario participa
    return db.query(Message).filter(
        or_(Message.sender_id == user_id, Message.recipient_id == user_id)
    ).order_by(Message.created_at.desc()).all()

from datetime import datetime

def mark_as_read(db: Session, user_id: int, sender_id: int):
    messages = db.query(Message).filter(
        Message.recipient_id == user_id,
        Message.sender_id == sender_id,
        Message.is_read == False
    ).all()
    now = datetime.now()
    for msg in messages:
        msg.is_read = True
        msg.read_at = now
    db.commit()
    return len(messages)
