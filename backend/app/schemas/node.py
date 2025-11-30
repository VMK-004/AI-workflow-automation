"""Node schemas"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class NodeBase(BaseModel):
    """Base node schema"""
    name: str = Field(..., min_length=1, max_length=255)
    node_type: str = Field(..., pattern="^(llm_call|http_request|faiss_search|db_write)$")
    config: Dict[str, Any] = Field(default_factory=dict)
    position_x: int = 0
    position_y: int = 0


class NodeCreate(NodeBase):
    """Schema for creating a node"""
    pass


class NodeUpdate(BaseModel):
    """Schema for updating a node"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    node_type: Optional[str] = Field(None, pattern="^(llm_call|http_request|faiss_search|db_write)$")
    config: Optional[Dict[str, Any]] = None
    position_x: Optional[int] = None
    position_y: Optional[int] = None


class NodeResponse(NodeBase):
    """Schema for node response"""
    id: str
    workflow_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
