from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class PostViewBase(BaseModel):
    post_id: int
    user_id: Optional[int] = None
    ip_address: Optional[str] = None

class PostViewCreate(PostViewBase):
    pass

class PostView(PostViewBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Aggregated Stats
class PostStats(BaseModel):
    post_id: int
    total_views: int
    unique_views: int
    likes_count: int
    comments_count: int

class UserAnalytics(BaseModel):
    user_id: int
    total_post_views: int
    follower_growth_weekly: int
    top_posts: List[PostStats]
