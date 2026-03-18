from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.session import Base

# Tabla de asociación para Posts y Hashtags
post_hashtags = Table(
    "post_hashtags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id", ondelete="CASCADE"), primary_key=True),
)

# Tabla de asociación para Comments y Hashtags
comment_hashtags = Table(
    "comment_hashtags",
    Base.metadata,
    Column("comment_id", Integer, ForeignKey("comments.id", ondelete="CASCADE"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id", ondelete="CASCADE"), primary_key=True),
)

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, index=True, nullable=False)

    # Relaciones
    posts = relationship("Post", secondary=post_hashtags, back_populates="hashtags")
    comments = relationship("Comment", secondary=comment_hashtags, back_populates="hashtags")
