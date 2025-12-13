"""User model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime

from sqlalchemy.orm import relationship

from app.db.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")
    workflow_runs = relationship("WorkflowRun", back_populates="user", cascade="all, delete-orphan")
    vector_collections = relationship("VectorCollection", back_populates="user", cascade="all, delete-orphan")
