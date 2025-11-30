"""FAISS search node handler"""
import logging
from typing import Dict, Any, Optional

from app.node_handlers.base import NodeHandler
from app.services.vector_service import get_vector_service
from app.exceptions import HandlerExecutionError

logger = logging.getLogger(__name__)


class FAISSSearchHandler(NodeHandler):
    """Handler for FAISS vector search nodes"""
    
    def __init__(self):
        """Initialize FAISS handler with vector service"""
        self.vector_service = get_vector_service()
    
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute FAISS vector search.
        
        Expected config:
            - collection_name: Name of the FAISS collection (required)
            - query: Search query text (required, supports templating)
            - top_k: Number of results to return (default: 5)
            - score_threshold: Minimum similarity score (optional)
            - metadata_filter: Filter results by metadata (optional)
        
        Args:
            config: Node configuration
            inputs: Input data from workflow
        
        Returns:
            Dict with search results
        """
        try:
            # Validate required config
            if "collection_name" not in config:
                raise HandlerExecutionError(
                    "FAISSSearchHandler",
                    "Missing required config field: 'collection_name'"
                )
            
            if "query" not in config:
                raise HandlerExecutionError(
                    "FAISSSearchHandler",
                    "Missing required config field: 'query'"
                )
            
            # Check if vector service is available
            if not self.vector_service.is_available():
                raise HandlerExecutionError(
                    "FAISSSearchHandler",
                    "Vector service not available. Embeddings model not loaded."
                )
            
            collection_name = config["collection_name"]
            query_template = config["query"]
            top_k = config.get("top_k", 5)
            score_threshold = config.get("score_threshold")
            metadata_filter = config.get("metadata_filter")
            
            # Validate parameters
            if not isinstance(top_k, int) or top_k <= 0:
                raise HandlerExecutionError(
                    "FAISSSearchHandler",
                    f"Invalid top_k value: {top_k}. Must be positive integer"
                )
            
            if score_threshold is not None:
                if not isinstance(score_threshold, (int, float)) or not (0.0 <= score_threshold <= 1.0):
                    raise HandlerExecutionError(
                        "FAISSSearchHandler",
                        f"Invalid score_threshold: {score_threshold}. Must be between 0.0 and 1.0"
                    )
            
            # Prepare template context
            template_context = self._prepare_template_context(inputs)
            
            # Render query template
            query = self._render_template(query_template, template_context)
            
            logger.info(f"Executing FAISS search in collection '{collection_name}'")
            logger.debug(f"Query: {query[:100]}...")
            
            # Get user_id from inputs (passed from execution context)
            # Collections are stored with user-scoped names: {user_id}_{collection_name}
            user_id = inputs.get("user_id")
            
            # Construct the actual collection name (user-scoped if user_id available)
            actual_collection_name = collection_name
            if user_id:
                actual_collection_name = f"{user_id}_{collection_name}"
                logger.debug(f"Using user-scoped collection name: '{actual_collection_name}' (user_id: {user_id})")
            
            # Perform search using the actual (user-scoped) collection name
            result = await self.vector_service.search(
                collection_name=actual_collection_name,
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                metadata_filter=metadata_filter
            )
            
            logger.info(f"FAISS search completed. Found {result['total_results']} results")
            
            return {
                "results": result["results"],
                "query": query,
                "collection_name": collection_name,
                "total_results": result["total_results"],
                "top_k": top_k,
                "score_threshold": score_threshold,
                "status": "success"
            }
            
        except HandlerExecutionError:
            raise
        except FileNotFoundError as e:
            logger.error(f"Collection not found: {str(e)}")
            raise HandlerExecutionError(
                "FAISSSearchHandler",
                f"Collection '{config.get('collection_name')}' not found. Create it first.",
                original_error=e
            )
        except Exception as e:
            logger.error(f"FAISS search failed: {str(e)}")
            raise HandlerExecutionError(
                "FAISSSearchHandler",
                f"Search execution failed: {str(e)}",
                original_error=e
            )
    
    def _prepare_template_context(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for template rendering"""
        context = {}
        
        # Add workflow input
        workflow_input = inputs.get("workflow_input", {})
        if isinstance(workflow_input, dict):
            context.update(workflow_input)
        
        # Add previous outputs
        previous_outputs = inputs.get("previous_outputs", {})
        if isinstance(previous_outputs, dict):
            context["outputs"] = previous_outputs
            # Flatten for easier access
            for node_id, output in previous_outputs.items():
                if isinstance(output, dict):
                    for key, value in output.items():
                        context[f"{node_id}_{key}"] = value
        
        return context
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render a string template using Python format"""
        if not isinstance(template, str):
            return str(template)
        
        try:
            return template.format(**context)
        except KeyError as e:
            logger.warning(f"Template variable not found: {e}. Using original template.")
            return template
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate node configuration"""
        if "collection_name" not in config:
            raise ValueError("Missing required field: collection_name")
        
        if "query" not in config:
            raise ValueError("Missing required field: query")
        
        if not isinstance(config["collection_name"], str):
            raise ValueError("collection_name must be a string")
        
        if not isinstance(config["query"], str):
            raise ValueError("query must be a string")
        
        if "top_k" in config:
            top_k = config["top_k"]
            if not isinstance(top_k, int) or top_k <= 0:
                raise ValueError("top_k must be a positive integer")
        
        if "score_threshold" in config:
            threshold = config["score_threshold"]
            if not isinstance(threshold, (int, float)) or not (0.0 <= threshold <= 1.0):
                raise ValueError("score_threshold must be between 0.0 and 1.0")
        
        return True
