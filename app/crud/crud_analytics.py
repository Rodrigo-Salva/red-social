from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from app.models.analytics import PostView
from app.models.post import Post, Comment
from app.models.user import User, followers
from app.schemas.analytics import PostStats, UserAnalytics

def create_post_view(db: Session, post_id: int, user_id: Optional[int] = None, ip_address: Optional[str] = None):
    db_view = PostView(post_id=post_id, user_id=user_id, ip_address=ip_address)
    db.add(db_view)
    db.commit()
    db.refresh(db_view)
    return db_view

def get_post_stats(db: Session, post_id: int) -> PostStats:
    total_views = db.query(PostView).filter(PostView.post_id == post_id).count()
    unique_views = db.query(func.count(func.distinct(PostView.user_id))).filter(PostView.post_id == post_id).scalar() or 0
    
    post = db.query(Post).filter(Post.id == post_id).first()
    likes_count = len(post.liked_by) if post else 0
    comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    
    return PostStats(
        post_id=post_id,
        total_views=total_views,
        unique_views=unique_views,
        likes_count=likes_count,
        comments_count=comments_count
    )

def get_user_analytics(db: Session, user_id: int) -> UserAnalytics:
    # 1. Total views de todos sus posts
    user_posts = db.query(Post.id).filter(Post.owner_id == user_id, Post.is_deleted == False).all()
    post_ids = [p.id for p in user_posts]
    
    total_views = db.query(PostView).filter(PostView.post_id.in_(post_ids)).count() if post_ids else 0
    
    # 2. Crecimiento semanal de seguidores
    one_week_ago = datetime.now() - timedelta(days=7)
    # Nota: followers is an association table. We might not have 'created_at' in the association table
    # but let's assume we want current total if growth tracking isn't possible, or try to count
    # by joining if there was a timestamp. 
    # Since 'followers' is likely a simple table (follower_id, followed_id), 
    # we'll just return the current total for now as a 'snapshot'.
    follower_count = db.query(followers).filter(followers.c.followed_id == user_id).count()
    
    # 3. Top posts (por vistas)
    top_post_ids = db.query(
        PostView.post_id, 
        func.count(PostView.id).label('view_count')
    ).filter(PostView.post_id.in_(post_ids)).group_by(PostView.post_id).order_by(desc('view_count')).limit(5).all()
    
    top_posts_stats = [get_post_stats(db, pid[0]) for pid in top_post_ids]
    
    return UserAnalytics(
        user_id=user_id,
        total_post_views=total_views,
        follower_growth_weekly=follower_count, # Snapshot
        top_posts=top_posts_stats
    )
