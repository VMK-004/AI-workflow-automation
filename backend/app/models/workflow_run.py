"""WorkflowRun model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class WorkflowRun(Base):
    """WorkflowRun model - execution instance of a workflow"""
    __tablename__ = "workflow_runs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="workflow_runs")
    user = relationship("User", back_populates="workflow_runs")
    node_executions = relationship("NodeExecution", back_populates="workflow_run", cascade="all, delete-orphan")
