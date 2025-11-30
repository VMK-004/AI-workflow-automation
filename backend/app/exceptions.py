"""Custom exceptions for the application"""
from fastapi import HTTPException, status


class GraphValidationError(HTTPException):
    """Base exception for graph validation errors"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class CycleError(GraphValidationError):
    """Raised when a cycle is detected in the workflow graph"""
    pass


class NoStartNodeError(GraphValidationError):
    """Raised when no start nodes are found in the workflow graph"""
    pass


class UnreachableNodeError(GraphValidationError):
    """Raised when some nodes are unreachable from start nodes"""
    pass


class DisconnectedGraphError(GraphValidationError):
    """Raised when the graph has disconnected components"""
    pass


class HandlerExecutionError(Exception):
    """Raised when a node handler fails to execute"""
    def __init__(self, handler_name: str, detail: str, original_error: Exception = None):
        self.handler_name = handler_name
        self.detail = detail
        self.original_error = original_error
        super().__init__(f"[{handler_name}] {detail}")
