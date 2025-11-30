"""Edge routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.schemas.edge import EdgeCreate, EdgeResponse
from app.models.user import User
from app.services.workflow_service import WorkflowService

router = APIRouter()


@router.get("/{workflow_id}/edges", response_model=List[EdgeResponse])
async def list_edges(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all edges in a workflow"""
    edges = await WorkflowService.list_edges(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id
    )
    return edges


@router.post("/{workflow_id}/edges", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
async def create_edge(
    workflow_id: str,
    edge_data: EdgeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new edge connecting two nodes in a workflow"""
    edge = await WorkflowService.create_edge(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
        edge_data=edge_data
    )
    return edge


@router.get("/{workflow_id}/edges/{edge_id}", response_model=EdgeResponse)
async def get_edge(
    workflow_id: str,
    edge_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get edge by ID"""
    edge = await WorkflowService.get_edge(
        db=db,
        workflow_id=workflow_id,
        edge_id=edge_id,
        user_id=current_user.id
    )
    
    if not edge:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edge not found"
        )
    
    return edge


@router.delete("/{workflow_id}/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    workflow_id: str,
    edge_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete edge"""
    success = await WorkflowService.delete_edge(
        db=db,
        workflow_id=workflow_id,
        edge_id=edge_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Edge not found"
        )
    
    return None
