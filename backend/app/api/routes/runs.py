"""Workflow runs API routes"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.execution_service import ExecutionService
from app.schemas.workflow_run import WorkflowRunExecuteRequest, WorkflowRunResponse

router = APIRouter()


@router.post("/{workflow_id}/execute", status_code=status.HTTP_201_CREATED)
async def execute_workflow(
    workflow_id: str,
    request: WorkflowRunExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Execute a workflow.
    
    Creates a new workflow run and executes all nodes in the workflow.
    Returns execution results including node outputs.
    """
    try:
        result = await ExecutionService.execute_workflow(
            db=db,
            workflow_id=workflow_id,
            user_id=current_user.id,
            input_data=request.input_data or {}
        )
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise


@router.get("/{workflow_id}/runs/{run_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(
    workflow_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get details of a specific workflow run.
    
    Returns workflow run information including status, input, output, and timing.
    """
    run_details = await ExecutionService.get_workflow_run_details(
        db=db,
        workflow_run_id=run_id,
        user_id=current_user.id
    )
    
    if not run_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow run not found"
        )
    
    return run_details
