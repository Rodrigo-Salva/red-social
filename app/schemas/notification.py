from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    type: str
    message: str
    post_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    recipient_id: int
    sender_id: Optional[int] = None

class NotificationUpdate(BaseModel):
    is_read: bool

class Notification(NotificationBase):
    id: int
    recipient_id: int
    sender_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
