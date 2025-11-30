"""Base node handler abstract class"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class NodeHandler(ABC):
    """Abstract base class for node handlers"""
    
    @abstractmethod
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute node logic
        
        Args:
            config: Node configuration from database
            inputs: Output from previous nodes {node_name: output_value}
        
        Returns:
            Dict with node output
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate node configuration (optional)"""
        return True
