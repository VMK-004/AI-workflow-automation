"""VectorCollection model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint

from sqlalchemy.orm import relationship

from app.db.database import Base


class VectorCollection(Base):
    """VectorCollection model - FAISS index metadata"""
    __tablename__ = "vector_collections"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    dimension = Column(Integer, nullable=False)
    index_path = Column(String(512), nullable=True)
    document_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="vector_collections")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_collection_name'),
    )
