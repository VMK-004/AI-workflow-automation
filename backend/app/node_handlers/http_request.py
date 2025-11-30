"""HTTP request node handler"""
import logging
from typing import Dict, Any, Optional
import httpx
import json

from app.node_handlers.base import NodeHandler
from app.exceptions import HandlerExecutionError

logger = logging.getLogger(__name__)


class HTTPRequestHandler(NodeHandler):
    """Handler for HTTP request nodes using httpx"""
    
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute HTTP request using httpx.
        
        Expected config:
            - url: Target URL (required, supports templating)
            - method: HTTP method (default: GET)
            - headers: Request headers (optional, supports templating)
            - body: Request body (optional, supports templating)
            - params: Query parameters (optional, supports templating)
            - timeout: Request timeout in seconds (default: 30)
            - follow_redirects: Whether to follow redirects (default: True)
            - verify_ssl: Whether to verify SSL certificates (default: True)
        
        Args:
            config: Node configuration
            inputs: Input data from workflow
        
        Returns:
            Dict with HTTP response data
        """
        try:
            # Validate and extract config
            if "url" not in config:
                raise HandlerExecutionError(
                    "HTTPRequestHandler",
                    "Missing required config field: 'url'"
                )
            
            method = config.get("method", "GET").upper()
            if method not in self.ALLOWED_METHODS:
                raise HandlerExecutionError(
                    "HTTPRequestHandler",
                    f"Invalid HTTP method: {method}. Allowed: {self.ALLOWED_METHODS}"
                )
            
            # Prepare template context
            template_context = self._prepare_template_context(inputs)
            
            # Render templated fields
            url = self._render_template(config["url"], template_context)
            headers = self._render_dict_template(config.get("headers", {}), template_context)
            params = self._render_dict_template(config.get("params", {}), template_context)
            body = self._render_body_template(config.get("body"), template_context)
            
            # Request options
            timeout = config.get("timeout", 30)
            follow_redirects = config.get("follow_redirects", True)
            verify_ssl = config.get("verify_ssl", True)
            
            logger.info(f"Executing HTTP {method} request to: {url}")
            logger.debug(f"Headers: {headers}")
            
            # Make HTTP request
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=follow_redirects,
                verify=verify_ssl
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=body if isinstance(body, dict) else None,
                    content=body if isinstance(body, (str, bytes)) else None
                )
            
            logger.info(f"HTTP request completed. Status: {response.status_code}")
            
            # Parse response
            response_data = self._parse_response(response)
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_data,
                "url": str(response.url),
                "method": method,
                "elapsed_ms": response.elapsed.total_seconds() * 1000,
                "status": "success" if response.is_success else "error"
            }
            
        except HandlerExecutionError:
            raise
        except httpx.TimeoutException as e:
            logger.error(f"HTTP request timeout: {str(e)}")
            raise HandlerExecutionError(
                "HTTPRequestHandler",
                f"Request timeout after {timeout}s",
                original_error=e
            )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            raise HandlerExecutionError(
                "HTTPRequestHandler",
                f"HTTP request failed: {str(e)}",
                original_error=e
            )
        except Exception as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise HandlerExecutionError(
                "HTTPRequestHandler",
                f"Request execution failed: {str(e)}",
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
            # Also flatten for easier access
            for node_id, output in previous_outputs.items():
                if isinstance(output, dict):
                    for key, value in output.items():
                        context[f"{node_id}_{key}"] = value
        
        return context
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render a string template using Python format"""
        if not isinstance(template, str):
            return template
        
        try:
            return template.format(**context)
        except KeyError as e:
            logger.warning(f"Template variable not found: {e}. Returning original template.")
            return template
    
    def _render_dict_template(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Render templates in dictionary values"""
        if not isinstance(data, dict):
            return {}
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._render_template(value, context)
            else:
                result[key] = value
        
        return result
    
    def _render_body_template(self, body: Any, context: Dict[str, Any]) -> Any:
        """Render body template (supports dict, str, or None)"""
        if body is None:
            return None
        
        if isinstance(body, dict):
            return self._render_dict_recursively(body, context)
        elif isinstance(body, str):
            return self._render_template(body, context)
        else:
            return body
    
    def _render_dict_recursively(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively render templates in nested dictionaries"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._render_template(value, context)
            elif isinstance(value, dict):
                result[key] = self._render_dict_recursively(value, context)
            elif isinstance(value, list):
                result[key] = [
                    self._render_template(item, context) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def _parse_response(self, response: httpx.Response) -> Any:
        """Parse HTTP response based on content type"""
        content_type = response.headers.get("content-type", "")
        
        # Try to parse JSON
        if "application/json" in content_type:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning text")
                return response.text
        
        # Try to parse as text
        if "text/" in content_type or "application/xml" in content_type:
            return response.text
        
        # Return raw bytes for binary content
        if response.content:
            # For binary, return base64 encoded string
            import base64
            return {
                "type": "binary",
                "content_type": content_type,
                "size": len(response.content),
                "data": base64.b64encode(response.content).decode('utf-8')
            }
        
        return None
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate node configuration"""
        if "url" not in config:
            raise ValueError("Missing required field: url")
        
        if not isinstance(config["url"], str):
            raise ValueError("url must be a string")
        
        if "method" in config:
            method = config["method"].upper()
            if method not in self.ALLOWED_METHODS:
                raise ValueError(f"Invalid method: {method}. Allowed: {self.ALLOWED_METHODS}")
        
        return True
