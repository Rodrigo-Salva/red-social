from typing import Optional
from pydantic import BaseModel, EmailStr

# Esquema compartido
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    username: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    is_private: Optional[bool] = False

# Para crear usuario (password requerido)
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Para actualizar usuario
class UserUpdate(UserBase):
    password: Optional[str] = None

# Para retornar usuario (sin password)
class User(UserBase):
    id: int
    is_two_factor_enabled: bool = False
    is_private: bool = False

    class Config:
        from_attributes = True
