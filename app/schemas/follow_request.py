from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

class FollowRequestStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class FollowRequestBase(BaseModel):
    recipient_id: int

class FollowRequestCreate(FollowRequestBase):
    pass

class FollowRequestUpdate(BaseModel):
    status: FollowRequestStatus

class FollowRequest(FollowRequestBase):
    id: int
    requester_id: int
    status: FollowRequestStatus
    created_at: datetime

    class Config:
        from_attributes = True
