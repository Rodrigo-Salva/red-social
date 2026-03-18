from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum

class FollowRequestStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class FollowRequest(Base):
    __tablename__ = "follow_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(Enum(FollowRequestStatus), default=FollowRequestStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    requester = relationship("User", foreign_keys=[requester_id], backref="sent_follow_requests")
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_follow_requests")

    __table_args__ = (UniqueConstraint('requester_id', 'recipient_id', 'status', name='_follow_request_uc'),)
