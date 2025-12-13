"""Execution history API routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.workflow_run_service import WorkflowRunService
from app.services.node_run_service import NodeRunService
from app.services.execution_service import ExecutionService
from app.schemas.workflow_run import (
    WorkflowRunListItemResponse,
    WorkflowRunListResponse,
    WorkflowRunDetailResponse
)

router = APIRouter()


@router.get("", response_model=WorkflowRunListResponse)
async def list_runs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WorkflowRunListResponse:
    """
    List all workflow runs for the current user.
    
    Returns list of workflow runs with:
    - id
    - workflow_id
    - workflow_name
    - status
    - started_at
    - completed_at
    - duration (computed)
    - final_output (optional preview)
    """
    # Fetch runs with workflow relationship
    runs = await WorkflowRunService.list_user_runs(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    # Count total runs
    total = await WorkflowRunService.count_user_runs(db=db, user_id=current_user.id)
    
    # Transform to list items with computed fields
    run_items = []
    for run in runs:
        # Calculate duration
        duration_seconds = None
        if run.completed_at and run.started_at:
            duration = (run.completed_at - run.started_at).total_seconds()
            duration_seconds = round(duration, 2)
        
        # Get output preview (first 100 chars)
        output_preview = None
        if run.output_data:
            import json
            output_str = json.dumps(run.output_data)
            if len(output_str) > 100:
                output_preview = output_str[:100] + "..."
            else:
                output_preview = output_str
        
        # Get workflow name
        workflow_name = run.workflow.name if run.workflow else "Unknown Workflow"
        
        run_items.append(WorkflowRunListItemResponse(
            id=str(run.id),
            workflow_id=str(run.workflow_id),
            workflow_name=workflow_name,
            status=run.status,
            started_at=run.started_at,
            completed_at=run.completed_at,
            duration_seconds=duration_seconds,
            final_output_preview=output_preview
        ))
    
    return WorkflowRunListResponse(runs=run_items, total=total)


@router.get("/{run_id}", response_model=WorkflowRunDetailResponse)
async def get_run_details(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WorkflowRunDetailResponse:
    """
    Get detailed information about a specific workflow run.
    
    Returns:
    - run info
    - node executions (with ordered timestamps)
    - error message if failed
    - final output
    """
    # Get run details (includes authorization check)
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





