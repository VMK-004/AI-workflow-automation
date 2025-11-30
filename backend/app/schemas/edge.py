"""Edge schemas"""
from datetime import datetime
from pydantic import BaseModel


class EdgeBase(BaseModel):
    """Base edge schema"""
    source_node_id: str
    target_node_id: str


class EdgeCreate(EdgeBase):
    """Schema for creating an edge"""
    pass


class EdgeResponse(EdgeBase):
    """Schema for edge response"""
    id: str
    workflow_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
