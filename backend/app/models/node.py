"""Node model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class Node(Base):
    """Node model"""
    __tablename__ = "nodes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    node_type = Column(String(50), nullable=False)  # llm_call, http_request, faiss_search, db_write
    config = Column(JSON, nullable=False, default={})
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="nodes")
    source_edges = relationship("Edge", foreign_keys="Edge.source_node_id", back_populates="source_node", cascade="all, delete-orphan")
    target_edges = relationship("Edge", foreign_keys="Edge.target_node_id", back_populates="target_node", cascade="all, delete-orphan")
    node_executions = relationship("NodeExecution", back_populates="node", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('workflow_id', 'name', name='uq_workflow_node_name'),
    )
