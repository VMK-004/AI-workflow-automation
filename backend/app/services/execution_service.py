"""Workflow execution service - Core execution engine"""
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.services.workflow_service import WorkflowService
from app.services.graph_service import GraphService
from app.services.workflow_run_service import WorkflowRunService
from app.services.node_run_service import NodeRunService
from app.services.node_handler_service import NodeHandlerService
from app.models.node import Node
from app.models.workflow_run import WorkflowRun
from app.models.node_execution import NodeExecution
from app.exceptions import GraphValidationError


class ExecutionService:
    """Service for workflow execution"""
    
    @staticmethod
    async def execute_workflow(
        db: AsyncSession,
        workflow_id: str,
        user_id: str,
        input_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow end-to-end.
        
        Steps:
        1. Load workflow, nodes, and edges
        2. Validate graph structure
        3. Determine execution order
        4. Create WorkflowRun record
        5. Execute nodes in order
        6. Update WorkflowRun status
        7. Return results
        
        Args:
            db: Database session
            workflow_id: ID of the workflow to execute
            user_id: ID of the user executing the workflow
            input_data: Input data for the workflow
        
        Returns:
            Dict with execution results:
            {
                "workflow_run_id": UUID,
                "status": "completed",
                "output": {...},
                "node_outputs": {...}
            }
        
        Raises:
            HTTPException: If workflow not found or validation fails
        """
        # 1. Load workflow data
        workflow = await WorkflowService.get_workflow(db, workflow_id, user_id)
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        nodes = await WorkflowService.list_nodes(db, workflow_id, user_id)
        edges = await WorkflowService.list_edges(db, workflow_id, user_id)
        
        if not nodes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow has no nodes to execute"
            )
        
        # 2. Validate graph structure
        try:
            validation = GraphService.validate_graph(nodes, edges, allow_disconnected=False)
        except GraphValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid workflow graph: {str(e)}"
            )
        
        # 3. Get execution order
        execution_order = validation["sorted_nodes"]
        
        # 4. Create WorkflowRun record
        workflow_run = await WorkflowRunService.create_run(
            db=db,
            workflow_id=workflow_id,
            user_id=user_id,
            input_data=input_data
        )
        
        # 5. Execute nodes in order
        try:
            result = await ExecutionService._execute_nodes(
                db=db,
                workflow_run_id=workflow_run.id,
                nodes=nodes,
                execution_order=execution_order,
                input_data=input_data or {},
                user_id=user_id
            )
            
            # 6. Update WorkflowRun to completed
            await WorkflowRunService.update_run_status(
                db=db,
                run_id=workflow_run.id,
                status="success",
                output_data=result["output"]
            )
            
            # 7. Get full workflow run with node executions
            stmt = select(WorkflowRun).where(WorkflowRun.id == workflow_run.id)
            result_query = await db.execute(stmt)
            final_run = result_query.scalar_one()
            
            # Get node executions
            stmt = select(NodeExecution).where(NodeExecution.workflow_run_id == workflow_run.id).order_by(NodeExecution.execution_order)
            result_query = await db.execute(stmt)
            node_executions = result_query.scalars().all()
            
            # Build response
            return {
                "id": str(final_run.id),
                "workflow_id": str(final_run.workflow_id),
                "user_id": str(final_run.user_id),
                "status": final_run.status,
                "started_at": final_run.started_at.isoformat(),
                "completed_at": final_run.completed_at.isoformat() if final_run.completed_at else None,
                "error_message": final_run.error_message,
                "input_data": final_run.input_data,
                "output_data": final_run.output_data,
                "node_executions": [
                    {
                        "id": str(ne.id),
                        "workflow_run_id": str(ne.workflow_run_id),
                        "node_id": str(ne.node_id),
                        "status": ne.status,
                        "input_data": ne.input_data,
                        "output_data": ne.output_data,
                        "error_message": ne.error_message,
                        "started_at": ne.started_at.isoformat() if ne.started_at else None,
                        "completed_at": ne.completed_at.isoformat() if ne.completed_at else None,
                        "execution_order": ne.execution_order,
                        "node_name": next((n.name for n in nodes if str(n.id) == str(ne.node_id)), None)
                    }
                    for ne in node_executions
                ]
            }
            
        except Exception as e:
            # Mark workflow run as failed
            await WorkflowRunService.update_run_status(
                db=db,
                run_id=workflow_run.id,
                status="failed",
                error_message=str(e)
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Workflow execution failed: {str(e)}"
            )
    
    @staticmethod
    async def _execute_nodes(
        db: AsyncSession,
        workflow_run_id: str,
        nodes: List[Node],
        execution_order: List[str],
        input_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute nodes in the given order.
        
        Args:
            db: Database session
            workflow_run_id: ID of the workflow run
            nodes: List of all nodes
            execution_order: List of node IDs in execution order
            input_data: Initial input data
            user_id: ID of the user executing the workflow
        
        Returns:
            Dict with node outputs and final output
        """
        # Create a map of node_id -> node for quick lookup
        node_map = {str(node.id): node for node in nodes}
        
        # Context to store intermediate results
        context = {
            "workflow_input": input_data,
            "node_outputs": {},
            "user_id": user_id
        }
        
        # Execute nodes in order
        for order_index, node_id in enumerate(execution_order):
            node = node_map.get(node_id)
            if not node:
                raise ValueError(f"Node {node_id} not found in node list")
            
            # Create NodeExecution record
            node_execution = await NodeRunService.create_node_run(
                db=db,
                workflow_run_id=workflow_run_id,
                node_id=node.id,
                execution_order=order_index
            )
            
            try:
                # Execute the node
                output = await ExecutionService._execute_single_node(
                    node=node,
                    context=context
                )
                
                # Store output in context
                context["node_outputs"][node_id] = output
                
                # Update NodeExecution to completed
                await NodeRunService.update_node_run(
                    db=db,
                    node_execution_id=node_execution.id,
                    status="completed",
                    output_data=output
                )
                
            except Exception as e:
                # Mark node execution as failed
                await NodeRunService.update_node_run(
                    db=db,
                    node_execution_id=node_execution.id,
                    status="failed",
                    error_message=str(e)
                )
                
                # Re-raise to fail the entire workflow
                raise Exception(f"Node '{node.name}' failed: {str(e)}")
        
        # Determine final output (last node's output)
        final_output = context["node_outputs"].get(execution_order[-1], {}) if execution_order else {}
        
        return {
            "output": final_output,
            "node_outputs": context["node_outputs"]
        }
    
    @staticmethod
    async def _execute_single_node(
        node: Node,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single node.
        
        Args:
            node: Node to execute
            context: Execution context with previous outputs
        
        Returns:
            Output from the node
        """
        # Prepare inputs for the node
        inputs = {
            "workflow_input": context.get("workflow_input", {}),
            "previous_outputs": context.get("node_outputs", {}),
            "user_id": context.get("user_id")  # Pass user_id for handlers that need it (e.g., FAISS search)
        }
        
        # Execute via NodeHandlerService
        output = await NodeHandlerService.execute_node(
            node_type=node.node_type,
            config=node.config,
            inputs=inputs
        )
        
        return output
    
    @staticmethod
    async def get_workflow_run_details(
        db: AsyncSession,
        workflow_run_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a workflow run.
        
        Args:
            db: Database session
            workflow_run_id: ID of the workflow run
            user_id: ID of the user (for authorization)
        
        Returns:
            Dict with workflow run details or None if not found
        """
        # Get workflow run
        workflow_run = await WorkflowRunService.get_run(db, workflow_run_id)
        
        if not workflow_run:
            return None
        
        # Verify user owns the workflow
        if workflow_run.user_id != user_id:
            return None
        
        return {
            "id": str(workflow_run.id),
            "workflow_id": str(workflow_run.workflow_id),
            "status": workflow_run.status,
            "input_data": workflow_run.input_data,
            "output_data": workflow_run.output_data,
            "error_message": workflow_run.error_message,
            "started_at": workflow_run.started_at,
            "completed_at": workflow_run.completed_at
        }
