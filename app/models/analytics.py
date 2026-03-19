from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class PostView(Base):
    __tablename__ = "post_views"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String, nullable=True)  # Para registrar vistas de invitados o control de spam
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Evitar múltiples registros del mismo usuario para el mismo post (opcional, depende de la política de analytics)
    # Por ahora permitimos múltiples para ver 'frecuencia', pero calcularemos 'uniques' en el CRUD.
    
    post = relationship("Post", backref="views")
    user = relationship("User")
