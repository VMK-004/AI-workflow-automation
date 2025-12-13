"""NodeExecution model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class NodeExecution(Base):
    """NodeExecution model - execution instance of a node"""
    __tablename__ = "node_executions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_run_id = Column(String(36), ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_order = Column(Integer, nullable=True)
    
    # Relationships
    workflow_run = relationship("WorkflowRun", back_populates="node_executions")
    node = relationship("Node", back_populates="node_executions")
