"""Workflow run service for managing workflow execution records"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_run import WorkflowRun
from app.models.workflow import Workflow


class WorkflowRunService:
    """Service for managing workflow run records"""
    
    @staticmethod
    async def create_run(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> WorkflowRun:
        """
        Create a new workflow run record.
        
        Args:
            db: Database session
            workflow_id: ID of the workflow to run
            user_id: ID of the user executing the workflow
            input_data: Input data for the workflow
        
        Returns:
            Created WorkflowRun object
        """
        new_run = WorkflowRun(
            workflow_id=workflow_id,
            user_id=user_id,
            status="running",
            input_data=input_data or {},
            started_at=datetime.utcnow()
        )
        
        db.add(new_run)
        await db.commit()
        await db.refresh(new_run)
        
        return new_run
    
    @staticmethod
    async def update_run_status(
        db: AsyncSession,
        run_id: str,
        status: str,
        output_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> WorkflowRun:
        """
        Update workflow run status and output.
        
        Args:
            db: Database session
            run_id: ID of the workflow run
            status: New status (running, completed, failed)
            output_data: Final output data (optional)
            error_message: Error message if failed (optional)
        
        Returns:
            Updated WorkflowRun object
        """
        stmt = select(WorkflowRun).where(WorkflowRun.id == run_id)
        result = await db.execute(stmt)
        run = result.scalar_one_or_none()
        
        if not run:
            raise ValueError(f"WorkflowRun {run_id} not found")
        
        run.status = status
        
        if output_data is not None:
            run.output_data = output_data
        
        if error_message is not None:
            run.error_message = error_message
        
        if status in ["completed", "failed"]:
            run.completed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(run)
        
        return run
    
    @staticmethod
    async def get_run(db: AsyncSession, run_id: str) -> Optional[WorkflowRun]:
        """Get workflow run by ID"""
        stmt = select(WorkflowRun).where(WorkflowRun.id == run_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_user_runs(
        db: AsyncSession,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[WorkflowRun]:
        """
        List all workflow runs for a user with workflow information.
        
        Args:
            db: Database session
            user_id: ID of the user
            limit: Maximum number of runs to return
            offset: Offset for pagination
        
        Returns:
            List of WorkflowRun objects with workflow relationship loaded
        """
        stmt = (
            select(WorkflowRun)
            .join(Workflow, WorkflowRun.workflow_id == Workflow.id)
            .where(WorkflowRun.user_id == user_id)
            .options(joinedload(WorkflowRun.workflow))
            .order_by(desc(WorkflowRun.started_at))
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars().unique().all())
    
    @staticmethod
    async def count_user_runs(db: AsyncSession, user_id: str) -> int:
        """Count total workflow runs for a user"""
        stmt = select(WorkflowRun).where(WorkflowRun.user_id == user_id)
        result = await db.execute(stmt)
        return len(list(result.scalars().all()))

