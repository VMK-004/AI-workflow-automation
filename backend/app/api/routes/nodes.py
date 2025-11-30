"""Node routes"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.schemas.node import NodeCreate, NodeUpdate, NodeResponse
from app.models.user import User
from app.services.workflow_service import WorkflowService

router = APIRouter()


@router.get("/{workflow_id}/nodes", response_model=List[NodeResponse])
async def list_nodes(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all nodes in a workflow"""
    nodes = await WorkflowService.list_nodes(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id
    )
    return nodes


@router.post("/{workflow_id}/nodes", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
async def create_node(
    workflow_id: str,
    node_data: NodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new node in a workflow"""
    node = await WorkflowService.create_node(
        db=db,
        workflow_id=workflow_id,
        user_id=current_user.id,
        node_data=node_data
    )
    return node


@router.get("/{workflow_id}/nodes/{node_id}", response_model=NodeResponse)
async def get_node(
    workflow_id: str,
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get node by ID"""
    node = await WorkflowService.get_node(
        db=db,
        workflow_id=workflow_id,
        node_id=node_id,
        user_id=current_user.id
    )
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    return node


@router.put("/{workflow_id}/nodes/{node_id}", response_model=NodeResponse)
async def update_node(
    workflow_id: str,
    node_id: str,
    node_data: NodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update node"""
    node = await WorkflowService.update_node(
        db=db,
        workflow_id=workflow_id,
        node_id=node_id,
        user_id=current_user.id,
        node_data=node_data
    )
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    return node


@router.delete("/{workflow_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_node(
    workflow_id: str,
    node_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete node"""
    success = await WorkflowService.delete_node(
        db=db,
        workflow_id=workflow_id,
        node_id=node_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    return None
