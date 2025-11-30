"""Workflow routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from app.models.user import User
from app.services.workflow_service import WorkflowService

router = APIRouter()


@router.get("", response_model=List[WorkflowResponse])
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all workflows for current user"""
    workflows = await WorkflowService.list_workflows(db, current_user.id)
    return workflows


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workflow"""
    workflow = await WorkflowService.create_workflow(
        db=db,
        user_id=current_user.id,
        workflow_data=workflow_data
    )
    return workflow


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workflow by ID"""
    workflow = await WorkflowService.get_workflow(db, workflow_id, current_user.id)
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update workflow"""
    workflow = await WorkflowService.update_workflow(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
        workflow_data=workflow_data
    )
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete workflow"""
    success = await WorkflowService.delete_workflow(db, workflow_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return None
