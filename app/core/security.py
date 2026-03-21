from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> tuple[str, str, datetime]:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    jti = str(uuid.uuid4())
    to_encode = {"exp": expire, "sub": subject, "jti": jti}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, jti, expire

def create_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    encoded_jwt = jwt.encode(
        {"exp": expires, "nbf": now, "sub": email, "type": "reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if decoded_token["type"] == "reset":
            return decoded_token["sub"]
    except jwt.JWTError:
        return None
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
