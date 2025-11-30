"""WorkflowRun schemas"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class WorkflowRunCreate(BaseModel):
    """Schema for creating a workflow run"""
    input_data: Optional[Dict[str, Any]] = None


class WorkflowRunExecuteRequest(BaseModel):
    """Schema for executing a workflow"""
    input_data: Optional[Dict[str, Any]] = None


class WorkflowRunResponse(BaseModel):
    """Schema for workflow run response"""
    id: str
    workflow_id: str
    user_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class NodeExecutionResponse(BaseModel):
    """Schema for node execution response"""
    id: str
    workflow_run_id: str
    node_id: str
    node_name: Optional[str] = None  # Added for display in frontend
    status: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_order: Optional[int] = None
    
    class Config:
        from_attributes = True


class WorkflowRunDetailResponse(WorkflowRunResponse):
    """Schema for detailed workflow run response with node executions"""
    node_executions: List[NodeExecutionResponse] = []


class WorkflowRunListItemResponse(BaseModel):
    """Schema for workflow run list item (summary)"""
    id: str
    workflow_id: str
    workflow_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    final_output_preview: Optional[str] = None  # First 100 chars of output
    
    class Config:
        from_attributes = True


class WorkflowRunListResponse(BaseModel):
    """Schema for list of workflow runs"""
    runs: List[WorkflowRunListItemResponse]
    total: int
