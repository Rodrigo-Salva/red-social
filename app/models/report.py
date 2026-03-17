from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    reason = Column(String, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    reporter = relationship("User", backref="reports_made")
    post = relationship("Post", backref="reports_received")
