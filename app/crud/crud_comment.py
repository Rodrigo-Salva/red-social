from sqlalchemy.orm import Session
from app.models.post import Comment
from app.schemas.post import CommentCreate

def create_comment(db: Session, comment: CommentCreate, owner_id: int):
    db_comment = Comment(**comment.dict(), owner_id=owner_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 100):
    return db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()
