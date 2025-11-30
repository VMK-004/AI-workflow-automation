"""Workflow service"""
from uuid import UUID
from typing import List
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.workflow import Workflow
from app.models.node import Node
from app.models.edge import Edge
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate
from app.schemas.node import NodeCreate, NodeUpdate
from app.schemas.edge import EdgeCreate


class WorkflowService:
    """Service for workflow operations"""
    
    @staticmethod
    async def create_workflow(db: AsyncSession, user_id: UUID, workflow_data: WorkflowCreate) -> Workflow:
        """Create a new workflow"""
        # Create new workflow linked to user
        new_workflow = Workflow(
            user_id=user_id,
            name=workflow_data.name,
            description=workflow_data.description,
            is_active=True
        )
        
        db.add(new_workflow)
        await db.commit()
        await db.refresh(new_workflow)
        
        return new_workflow
    
    @staticmethod
    async def get_workflow(db: AsyncSession, workflow_id: UUID, user_id: UUID) -> Workflow | None:
        """Get workflow by ID (only if it belongs to the user)"""
        stmt = select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == user_id
        )
        result = await db.execute(stmt)
        workflow = result.scalar_one_or_none()
        
        return workflow
    
    @staticmethod
    async def list_workflows(db: AsyncSession, user_id: UUID) -> List[Workflow]:
        """List all workflows for a user"""
        stmt = select(Workflow).where(Workflow.user_id == user_id).order_by(Workflow.created_at.desc())
        result = await db.execute(stmt)
        workflows = result.scalars().all()
        
        return list(workflows)
    
    @staticmethod
    async def update_workflow(db: AsyncSession, workflow_id: UUID, user_id: UUID, workflow_data: WorkflowUpdate) -> Workflow | None:
        """Update workflow (only if it belongs to the user)"""
        # Fetch workflow
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        
        if not workflow:
            return None
        
        # Update fields (only if provided)
        if workflow_data.name is not None:
            workflow.name = workflow_data.name
        
        if workflow_data.description is not None:
            workflow.description = workflow_data.description
        
        if workflow_data.is_active is not None:
            workflow.is_active = workflow_data.is_active
        
        workflow.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(workflow)
        
        return workflow
    
    @staticmethod
    async def delete_workflow(db: AsyncSession, workflow_id: UUID, user_id: UUID) -> bool:
        """Delete workflow (only if it belongs to the user)"""
        # Fetch workflow to verify ownership
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        
        if not workflow:
            return False
        
        # Delete workflow (cascade will handle nodes and edges)
        await db.delete(workflow)
        await db.commit()
        
        return True
    
    # Node operations
    @staticmethod
    async def create_node(db: AsyncSession, workflow_id: UUID, user_id: UUID, node_data: NodeCreate) -> Node:
        """Create a new node in a workflow"""
        # Verify workflow ownership first
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Create new node
        new_node = Node(
            workflow_id=workflow_id,
            name=node_data.name,
            node_type=node_data.node_type,
            config=node_data.config,
            position_x=node_data.position_x,
            position_y=node_data.position_y
        )
        
        db.add(new_node)
        await db.commit()
        await db.refresh(new_node)
        
        return new_node
    
    @staticmethod
    async def get_node(db: AsyncSession, workflow_id: UUID, node_id: UUID, user_id: UUID) -> Node | None:
        """Get node by ID (verify workflow ownership)"""
        # Verify workflow ownership first
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        # Get node within this workflow
        stmt = select(Node).where(
            Node.id == node_id,
            Node.workflow_id == workflow_id
        )
        result = await db.execute(stmt)
        node = result.scalar_one_or_none()
        
        return node
    
    @staticmethod
    async def list_nodes(db: AsyncSession, workflow_id: UUID, user_id: UUID) -> List[Node]:
        """List all nodes in a workflow"""
        # Verify workflow ownership first
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # List nodes in this workflow
        stmt = select(Node).where(Node.workflow_id == workflow_id).order_by(Node.created_at)
        result = await db.execute(stmt)
        nodes = result.scalars().all()
        
        return list(nodes)
    
    @staticmethod
    async def update_node(db: AsyncSession, workflow_id: UUID, node_id: UUID, user_id: UUID, node_data: NodeUpdate) -> Node | None:
        """Update node (verify workflow ownership)"""
        # Get node (with workflow ownership check)
        node = await WorkflowService.get_node(db, workflow_id, node_id, user_id)
        
        if not node:
            return None
        
        # Update fields (only if provided)
        if node_data.name is not None:
            node.name = node_data.name
        
        if node_data.node_type is not None:
            node.node_type = node_data.node_type
        
        if node_data.config is not None:
            node.config = node_data.config
        
        if node_data.position_x is not None:
            node.position_x = node_data.position_x
        
        if node_data.position_y is not None:
            node.position_y = node_data.position_y
        
        node.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(node)
        
        return node
    
    @staticmethod
    async def delete_node(db: AsyncSession, workflow_id: UUID, node_id: UUID, user_id: UUID) -> bool:
        """Delete node (verify workflow ownership)"""
        # Get node (with workflow ownership check)
        node = await WorkflowService.get_node(db, workflow_id, node_id, user_id)
        
        if not node:
            return False
        
        # Delete node
        await db.delete(node)
        await db.commit()
        
        return True
    
    # Edge operations
    @staticmethod
    async def create_edge(db: AsyncSession, workflow_id: UUID, user_id: UUID, edge_data: EdgeCreate) -> Edge:
        """Create a new edge connecting two nodes"""
        # Verify workflow ownership first
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Validate source node belongs to this workflow
        source_node = await WorkflowService.get_node(db, workflow_id, edge_data.source_node_id, user_id)
        if not source_node:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source node does not belong to this workflow"
            )
        
        # Validate target node belongs to this workflow
        target_node = await WorkflowService.get_node(db, workflow_id, edge_data.target_node_id, user_id)
        if not target_node:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target node does not belong to this workflow"
            )
        
        # Create edge
        new_edge = Edge(
            workflow_id=workflow_id,
            source_node_id=edge_data.source_node_id,
            target_node_id=edge_data.target_node_id
        )
        
        db.add(new_edge)
        await db.commit()
        await db.refresh(new_edge)
        
        return new_edge
    
    @staticmethod
    async def get_edge(db: AsyncSession, workflow_id: UUID, edge_id: UUID, user_id: UUID) -> Edge | None:
        """Get edge by ID (verify workflow ownership)"""
        # Verify workflow ownership first
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            return None
        
        # Get edge within this workflow
        stmt = select(Edge).where(
            Edge.id == edge_id,
            Edge.workflow_id == workflow_id
        )
        result = await db.execute(stmt)
        edge = result.scalar_one_or_none()
        
        return edge
    
    @staticmethod
    async def list_edges(db: AsyncSession, workflow_id: UUID, user_id: UUID) -> List[Edge]:
        """List all edges in a workflow"""
        # Verify workflow ownership first
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # List edges in this workflow
        stmt = select(Edge).where(Edge.workflow_id == workflow_id).order_by(Edge.created_at)
        result = await db.execute(stmt)
        edges = result.scalars().all()
        
        return list(edges)
    
    @staticmethod
    async def delete_edge(db: AsyncSession, workflow_id: UUID, edge_id: UUID, user_id: UUID) -> bool:
        """Delete edge (verify workflow ownership)"""
        # Get edge (with workflow ownership check)
        edge = await WorkflowService.get_edge(db, workflow_id, edge_id, user_id)
        
        if not edge:
            return False
        
        # Delete edge
        await db.delete(edge)
        await db.commit()
        
        return True
