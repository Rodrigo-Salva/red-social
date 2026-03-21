from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, select, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.user import User
from app.models.post import Post

class PollVote(Base):
    __tablename__ = "poll_votes"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id", ondelete="CASCADE"))
    option_id = Column(Integer, ForeignKey("poll_options.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    __table_args__ = (UniqueConstraint('poll_id', 'user_id', name='unique_vote_per_user'),)

    option = relationship("PollOption", back_populates="votes")
    user = relationship("User")

class PollOption(Base):
    __tablename__ = "poll_options"

    id = Column(Integer, primary_key=True, index=True)
    poll_id = Column(Integer, ForeignKey("polls.id", ondelete="CASCADE"))
    text = Column(String, nullable=False)
    
    poll = relationship("Poll", back_populates="options")
    votes = relationship("PollVote", back_populates="option", cascade="all, delete-orphan")

    @hybrid_property
    def votes_count(self) -> int:
        return len(self.votes)

class Poll(Base):
    __tablename__ = "polls"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="poll")
    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")
