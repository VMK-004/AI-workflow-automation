"""Node run service for managing node execution records"""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.node_execution import NodeExecution


class NodeRunService:
    """Service for managing node execution records"""
    
    @staticmethod
    async def create_node_run(
        db: AsyncSession,
        workflow_run_id: str,
        node_id: str,
        execution_order: int
    ) -> NodeExecution:
        """
        Create a new node execution record.
        
        Args:
            db: Database session
            workflow_run_id: ID of the workflow run
            node_id: ID of the node being executed
            execution_order: Order in which this node is executed
        
        Returns:
            Created NodeExecution object
        """
        node_execution = NodeExecution(
            workflow_run_id=workflow_run_id,
            node_id=node_id,
            status="running",
            execution_order=execution_order,
            started_at=datetime.utcnow()
        )
        
        db.add(node_execution)
        await db.commit()
        await db.refresh(node_execution)
        
        return node_execution
    
    @staticmethod
    async def update_node_run(
        db: AsyncSession,
        node_execution_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> NodeExecution:
        """
        Update node execution status and output.
        
        Args:
            db: Database session
            node_execution_id: ID of the node execution
            status: New status (running, completed, failed)
            output_data: Output data from the node (optional)
            error_message: Error message if failed (optional)
        
        Returns:
            Updated NodeExecution object
        """
        stmt = select(NodeExecution).where(NodeExecution.id == node_execution_id)
        result = await db.execute(stmt)
        node_execution = result.scalar_one_or_none()
        
        if not node_execution:
            raise ValueError(f"NodeExecution {node_execution_id} not found")
        
        node_execution.status = status
        
        if output_data is not None:
            node_execution.output_data = output_data
        
        if error_message is not None:
            node_execution.error_message = error_message
        
        if status in ["completed", "failed"]:
            node_execution.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(node_execution)
        
        return node_execution
    
    @staticmethod
    async def get_node_run(db: AsyncSession, node_execution_id: str) -> Optional[NodeExecution]:
        """Get node execution by ID"""
        stmt = select(NodeExecution).where(NodeExecution.id == node_execution_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

