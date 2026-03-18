from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from app.models.user import User
from app.models.post import Post
from app.schemas.post import PostCreate

def get_posts(
    db: Session, 
    current_user_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100, 
    only_images: bool = False,
    sort_by_popularity: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    from app.models.block import Block
    query = db.query(Post).join(User, Post.owner_id == User.id).filter(Post.is_deleted == False)
    
    # Excluir posts de usuarios privados (a menos que los sigas, pero en 'descubrir' usualmente no se muestran)
    # Por ahora, si no hay current_user_id, solo mostrar públicos.
    if current_user_id:
        # Excluir bloqueados
        blocked_ids = db.query(Block.blocked_id).filter(Block.blocker_id == current_user_id)
        blocker_ids = db.query(Block.blocker_id).filter(Block.blocked_id == current_user_id)
        query = query.filter(~Post.owner_id.in_(blocked_ids))
        query = query.filter(~Post.owner_id.in_(blocker_ids))
        
        # Mostrar mis propios posts, posts de gente que sigo (aunque sean privados), y posts públicos de otros.
        from app.models.user import followers
        is_following = db.query(followers.c.followed_id).filter(followers.c.follower_id == current_user_id)
        
        query = query.filter(
            (User.is_private == False) | 
            (Post.owner_id == current_user_id) |
            (Post.owner_id.in_(is_following))
        )
    else:
        query = query.filter(User.is_private == False)
    
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
    from app.models.block import Block
    followed_ids = [u.id for u in user.following]
    followed_ids.append(user.id)
    
    # Excluir usuarios que me han bloqueado o que yo he bloqueado
    blocked_ids = db.query(Block.blocked_id).filter(Block.blocker_id == user.id)
    blocker_ids = db.query(Block.blocker_id).filter(Block.blocked_id == user.id)
    
    return db.query(Post).filter(
        Post.is_deleted == False,
        Post.owner_id.in_(followed_ids),
        ~Post.owner_id.in_(blocked_ids),
        ~Post.owner_id.in_(blocker_ids)
    ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

def get_feed_count(db: Session, user: User) -> int:
    from app.models.block import Block
    followed_ids = [u.id for u in user.following]
    followed_ids.append(user.id)
    
    blocked_ids = db.query(Block.blocked_id).filter(Block.blocker_id == user.id)
    blocker_ids = db.query(Block.blocker_id).filter(Block.blocked_id == user.id)
    
    return db.query(Post).filter(
        Post.is_deleted == False,
        Post.owner_id.in_(followed_ids),
        ~Post.owner_id.in_(blocked_ids),
        ~Post.owner_id.in_(blocker_ids)
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
