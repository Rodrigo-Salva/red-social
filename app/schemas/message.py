from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class MessageBase(BaseModel):
    content: str

# Properties to receive on message creation
class MessageCreate(MessageBase):
    recipient_id: int

# Properties to receive on message update
class MessageUpdate(MessageBase):
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None

# Properties shared by models stored in DB
class MessageInDBBase(MessageBase):
    id: int
    sender_id: int
    recipient_id: int
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True

# Properties to return to client
class Message(MessageInDBBase):
    pass
