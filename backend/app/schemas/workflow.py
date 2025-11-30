"""Workflow schemas"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class WorkflowBase(BaseModel):
    """Base workflow schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    """Schema for creating a workflow"""
    pass


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    """Schema for workflow response"""
    id: str
    user_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
