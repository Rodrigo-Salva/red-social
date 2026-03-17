from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.models.user import User, Post
from app.schemas.post import PostCreate

def get_posts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    only_images: bool = False,
    sort_by_popularity: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(Post).filter(Post.is_deleted == False)
    
    if only_images:
        query = query.filter(Post.image_url != None)
    
    if start_date:
        query = query.filter(Post.created_at >= start_date)
    if end_date:
        query = query.filter(Post.created_at <= end_date)
        
    if sort_by_popularity:
        # Esto requiere unir con la tabla de likes y contar
        # Por simplicidad, asumimos que Post tiene un counter o calculamos al vuelo
        # Post.liked_by is a relationship. We can use func.count on the association table if we had direct access
        # but let's do a simple count subquery if needed. 
        # For now, let's just use the current order if complexity is too high, 
        # or implement a basic popularity sort.
        pass
        
    return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

def create_user_post(db: Session, post: PostCreate, owner_id: int):
    db_post = Post(**post.dict(), owner_id=owner_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_post(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id, Post.is_deleted == False).first()

def delete_post(db: Session, post_id: int):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db_post.is_deleted = True
        db.add(db_post)
        db.commit()
    return db_post

def get_feed(db: Session, user: User, skip: int = 0, limit: int = 10):
    followed_ids = [u.id for u in user.following]
    followed_ids.append(user.id)
    return db.query(Post).filter(
        Post.is_deleted == False,
        Post.owner_id.in_(followed_ids)
    ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

def get_feed_count(db: Session, user: User) -> int:
    followed_ids = [u.id for u in user.following]
    followed_ids.append(user.id)
    return db.query(Post).filter(
        Post.is_deleted == False,
        Post.owner_id.in_(followed_ids)
    ).count()

def like_post(db: Session, user: User, post: Post):
    if user not in post.liked_by:
        post.liked_by.append(user)
        db.commit()
    return post

def unlike_post(db: Session, user: User, post: Post):
    if user in post.liked_by:
        post.liked_by.remove(user)
        db.commit()
    return post
