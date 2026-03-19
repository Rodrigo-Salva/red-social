from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Shared properties
class StoryBase(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None

# Properties to receive on story creation
class StoryCreate(StoryBase):
    image_url: str  # Requerida para historias

# Properties shared by models stored in DB
class StoryInDBBase(StoryBase):
    id: int
    owner_id: int
    created_at: datetime
    expires_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True

# Properties to return to client
class Story(StoryInDBBase):
    pass
