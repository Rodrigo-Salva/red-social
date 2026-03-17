from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    is_2fa_required: bool = False
    temp_token_2fa: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    jti: Optional[str] = None
