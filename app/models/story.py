from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.db.session import Base

class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(String, nullable=True)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_deleted = Column(Boolean, default=False)

    owner = relationship("User", backref="stories")

    @property
    def is_active(self) -> bool:
        return not self.is_deleted and self.expires_at > datetime.now(self.expires_at.tzinfo)
