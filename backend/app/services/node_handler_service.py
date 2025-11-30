"""Node handler factory service"""
from typing import Dict, Type, Any

from app.node_handlers.base import NodeHandler
from app.node_handlers.llm_call import LLMCallHandler
from app.node_handlers.http_request import HTTPRequestHandler
from app.node_handlers.faiss_search import FAISSSearchHandler
from app.node_handlers.db_write import DBWriteHandler


class NodeHandlerService:
    """Service for dispatching node execution to appropriate handlers"""
    
    _handlers: Dict[str, Type[NodeHandler]] = {
        "llm_call": LLMCallHandler,
        "http_request": HTTPRequestHandler,
        "faiss_search": FAISSSearchHandler,
        "db_write": DBWriteHandler,
    }
    
    @classmethod
    def get_handler(cls, node_type: str) -> NodeHandler:
        """
        Get handler instance for node type.
        
        Args:
            node_type: Type of node (llm_call, http_request, etc.)
        
        Returns:
            Handler instance
        
        Raises:
            ValueError: If node type is unknown
        """
        handler_class = cls._handlers.get(node_type)
        if handler_class is None:
            raise ValueError(f"Unknown node type: {node_type}")
        return handler_class()
    
    @classmethod
    async def execute_node(cls, node_type: str, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a node by dispatching to the appropriate handler.
        
        Args:
            node_type: Type of node to execute
            config: Node configuration from database
            inputs: Input data from previous nodes
        
        Returns:
            Output data from the node
        
        Raises:
            ValueError: If node type is unknown
            Exception: If node execution fails
        """
        handler = cls.get_handler(node_type)
        output = await handler.execute(config, inputs)
        return output
    
    @classmethod
    def register_handler(cls, node_type: str, handler_class: Type[NodeHandler]):
        """Register a new node handler type"""
        cls._handlers[node_type] = handler_class
    
    @classmethod
    def list_node_types(cls) -> list[str]:
        """List all available node types"""
        return list(cls._handlers.keys())


# Backward compatibility alias
NodeHandlerFactory = NodeHandlerService
