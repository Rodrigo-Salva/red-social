from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

def create_notification(db: Session, notification: NotificationCreate):
    db_obj = Notification(
        recipient_id=notification.recipient_id,
        sender_id=notification.sender_id,
        type=notification.type,
        message=notification.message,
        post_id=notification.post_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    return db.query(Notification).filter(Notification.recipient_id == user_id)\
        .order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_as_read(db: Session, notification_id: int):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification
