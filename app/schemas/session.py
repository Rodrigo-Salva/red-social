from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class UserSessionBase(BaseModel):
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    is_active: bool
    created_at: datetime
    expires_at: datetime

class UserSession(UserSessionBase):
    id: int
    token_jti: str

    class Config:
        from_attributes = True

class SessionRevoke(BaseModel):
    session_id: int
