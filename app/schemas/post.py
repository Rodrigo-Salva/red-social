from typing import Optional, List
from pydantic import BaseModel, Field

# Esquema compartido
class PostBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

# Para crear post
class PostCreate(PostBase):
    title: str = Field(...)
    content: str = Field(...)
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

# Esquema para Comentarios
class CommentBase(BaseModel):
    content: str
    post_id: int

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# Para retornar post mejorado
class Post(PostBase):
    id: int
    owner_id: int
    likes_count: int = 0
    comments: List[Comment] = []

    @classmethod
    def from_orm(cls, obj):
        # Mapeo manual si es necesario o usar computed fields
        data = super().from_orm(obj)
        data.likes_count = len(obj.liked_by)
        return data

    class Config:
        from_attributes = True
