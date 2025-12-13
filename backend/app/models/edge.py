"""Edge model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint

from sqlalchemy.orm import relationship

from app.db.database import Base


class Edge(Base):
    """Edge model - connects two nodes"""
    __tablename__ = "edges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    target_node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="edges")
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="source_edges")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="target_edges")
    
    __table_args__ = (
        UniqueConstraint('source_node_id', 'target_node_id', name='uq_source_target'),
    )
