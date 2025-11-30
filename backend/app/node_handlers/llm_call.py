"""LLM call node handler"""
import logging
from typing import Dict, Any

from app.node_handlers.base import NodeHandler
from app.services.llm_service import LLMService
from app.exceptions import HandlerExecutionError

logger = logging.getLogger(__name__)


class LLMCallHandler(NodeHandler):
    """Handler for LLM call nodes using Qwen model via LangChain"""
    
    def __init__(self):
        """Initialize LLM handler with service"""
        self.llm_service = LLMService()
    
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute LLM call using Qwen model.
        
        Expected config:
            - prompt_template: Template string with {variable} placeholders (required)
            - temperature: Sampling temperature 0.0-1.0 (default: 0.7)
            - max_tokens: Maximum tokens to generate (default: 256)
            - top_p: Nucleus sampling parameter (optional)
            - top_k: Top-k sampling parameter (optional)
        
        The template can reference:
            - Any key from workflow_input
            - Any key from previous node outputs
            - Variables specified in config
        
        Args:
            config: Node configuration
            inputs: Input data containing workflow_input and previous_outputs
        
        Returns:
            Dict with LLM response and metadata
        """
        try:
            # Validate required config
            if "prompt_template" not in config:
                raise HandlerExecutionError(
                    "LLMCallHandler",
                    "Missing required config field: 'prompt_template'"
                )
            
            prompt_template = config["prompt_template"]
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("max_tokens", 256)
            
            # Validate parameters
            if not isinstance(temperature, (int, float)) or not (0.0 <= temperature <= 2.0):
                raise HandlerExecutionError(
                    "LLMCallHandler",
                    f"Invalid temperature value: {temperature}. Must be between 0.0 and 2.0"
                )
            
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                raise HandlerExecutionError(
                    "LLMCallHandler",
                    f"Invalid max_tokens value: {max_tokens}. Must be positive integer"
                )
            
            # Prepare template variables
            template_vars = self._prepare_template_variables(config, inputs)
            
            logger.info(f"Executing LLM call with template length: {len(prompt_template)}")
            logger.debug(f"Template variables: {list(template_vars.keys())}")
            
            # Generate text using LLM service
            result = await self.llm_service.generate_with_template(
                template=prompt_template,
                variables=template_vars,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=config.get("top_p"),
                top_k=config.get("top_k")
            )
            
            logger.info(f"LLM generation successful. Tokens used: {result.get('tokens_used', 0)}")
            
            return {
                "response": result["generated_text"],
                "model": result["model_name"],
                "tokens_used": result["tokens_used"],
                "input_tokens": result.get("input_tokens", 0),
                "output_tokens": result.get("output_tokens", 0),
                "temperature": temperature,
                "max_tokens": max_tokens,
                "status": result.get("status", "success")
            }
            
        except HandlerExecutionError:
            raise
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            raise HandlerExecutionError(
                "LLMCallHandler",
                f"LLM execution failed: {str(e)}",
                original_error=e
            )
    
    def _prepare_template_variables(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare variables for template rendering.
        
        Priority order (later overrides earlier):
        1. workflow_input
        2. previous_outputs (flattened)
        3. variables from config
        
        Args:
            config: Node configuration
            inputs: Input data
        
        Returns:
            Dict of template variables
        """
        template_vars = {}
        
        # Add workflow input
        workflow_input = inputs.get("workflow_input", {})
        if isinstance(workflow_input, dict):
            template_vars.update(workflow_input)
        
        # Add previous outputs (flattened)
        previous_outputs = inputs.get("previous_outputs", {})
        if isinstance(previous_outputs, dict):
            for node_id, output in previous_outputs.items():
                if isinstance(output, dict):
                    # Add each output field with node_id prefix
                    for key, value in output.items():
                        template_vars[f"{node_id}_{key}"] = value
                else:
                    template_vars[node_id] = output
        
        # Add variables from config (highest priority)
        config_vars = config.get("variables", {})
        if isinstance(config_vars, dict):
            template_vars.update(config_vars)
        
        return template_vars
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate node configuration.
        
        Args:
            config: Node configuration
        
        Returns:
            True if valid
        
        Raises:
            ValueError: If configuration is invalid
        """
        if "prompt_template" not in config:
            raise ValueError("Missing required field: prompt_template")
        
        if not isinstance(config["prompt_template"], str):
            raise ValueError("prompt_template must be a string")
        
        if "temperature" in config:
            temp = config["temperature"]
            if not isinstance(temp, (int, float)) or not (0.0 <= temp <= 2.0):
                raise ValueError("temperature must be between 0.0 and 2.0")
        
        if "max_tokens" in config:
            max_tok = config["max_tokens"]
            if not isinstance(max_tok, int) or max_tok <= 0:
                raise ValueError("max_tokens must be a positive integer")
        
        return True
