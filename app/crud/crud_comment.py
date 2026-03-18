from sqlalchemy.orm import Session
from app.models.post import Comment
from app.schemas.post import CommentCreate
from app.core.text_parser import extract_hashtags, extract_mentions
from app.models.hashtag import Hashtag

def create_comment(db: Session, comment: CommentCreate, owner_id: int):
    db_comment = Comment(**comment.dict(), owner_id=owner_id)
    db.add(db_comment)
    
    # Procesar Hashtags
    tags = extract_hashtags(comment.content)
    for tag in tags:
        hashtag = db.query(Hashtag).filter(Hashtag.tag == tag).first()
        if not hashtag:
            hashtag = Hashtag(tag=tag)
            db.add(hashtag)
            db.flush()
        db_comment.hashtags.append(hashtag)
        
    db.commit()
    db.refresh(db_comment)
    
    # Procesar Menciones
    from app.crud.crud_user import get_user_by_username
    from app.crud.crud_notification import create_notification
    from app.schemas.notification import NotificationCreate
    
    usernames = extract_mentions(comment.content)
    for username in usernames:
        user = get_user_by_username(db, username=username)
        if user and user.id != owner_id:
            notification_in = NotificationCreate(
                recipient_id=user.id,
                sender_id=owner_id,
                type="mention",
                message=f"Te han mencionado en un comentario",
                post_id=db_comment.post_id
            )
            create_notification(db, notification=notification_in)
            
    return db_comment

def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 100):
    return db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()
