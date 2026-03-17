from pydantic import BaseModel
from typing import Optional

class TwoFactorToken(BaseModel):
    token: str

class TwoFactorSetupResponse(BaseModel):
    secret: str
    otpauth_url: str
    qr_code_base64: str

class TwoFactorVerify(BaseModel):
    token: str

class TwoFactorStatus(BaseModel):
    is_enabled: bool
