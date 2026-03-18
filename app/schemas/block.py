from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class BlockBase(BaseModel):
    blocked_id: int

class BlockCreate(BlockBase):
    pass

class Block(BlockBase):
    id: int
    blocker_id: int
    created_at: datetime

    class Config:
        from_attributes = True
