from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.user import likes

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_deleted = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    
    # Usuarios que le dieron like
    liked_by = relationship("User", secondary=likes, backref="liked_posts")
    
    # Hashtags asociados
    hashtags = relationship("Hashtag", secondary="post_hashtags", back_populates="posts")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", backref="comments")
    post = relationship("Post", back_populates="comments")
    
    # Hashtags asociados
    hashtags = relationship("Hashtag", secondary="comment_hashtags", back_populates="comments")
