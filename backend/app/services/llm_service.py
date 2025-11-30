"""LLM service for Qwen model integration via Ollama"""
import logging
import json
from typing import Dict, Any, Optional, List
import httpx

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Qwen model via Ollama"""
    
    def __init__(self):
        """Initialize LLM service"""
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen3:0.6b"  # Qwen 3 0.6B model
        self.timeout = 60.0  # 60 seconds timeout
    
    @staticmethod
    def _format_template_value(value: Any) -> str:
        """
        Intelligently format a template value for better readability.
        
        Handles:
        - Lists of dicts with 'text' field (FAISS results): Extracts text and joins with newlines
        - Lists of strings: Joins with newlines
        - Lists of other types: Joins with newlines (converted to string)
        - Dicts: Pretty-printed JSON
        - Other types: Standard string conversion
        
        Args:
            value: The value to format
        
        Returns:
            Formatted string representation
        """
        # Handle lists
        if isinstance(value, list):
            if not value:
                return ""
            
            # Check if it's a list of dicts with 'text' field (FAISS results pattern)
            if all(isinstance(item, dict) and 'text' in item for item in value):
                # Extract text from each dict and join with newlines
                texts = [str(item.get('text', '')) for item in value]
                return '\n'.join(texts)
            
            # Check if it's a list of strings
            elif all(isinstance(item, str) for item in value):
                return '\n'.join(value)
            
            # List of other types - convert each to string and join
            else:
                return '\n'.join(str(item) for item in value)
        
        # Handle dicts - pretty print as JSON
        elif isinstance(value, dict):
            try:
                return json.dumps(value, indent=2, ensure_ascii=False)
            except (TypeError, ValueError):
                # Fallback if JSON serialization fails
                return str(value)
        
        # Handle None
        elif value is None:
            return ""
        
        # Default: convert to string
        else:
            return str(value)
    
    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using Qwen model via Ollama.
        
        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
        
        Returns:
            Dict with generated text and metadata
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare request payload
                payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    }
                }
                
                logger.info(f"Calling Ollama API with prompt length: {len(prompt)}")
                
                # Make request to Ollama
                response = await client.post(self.ollama_url, json=payload)
                response.raise_for_status()
                
                # Parse response
                data = response.json()
                generated_text = data.get("response", "")
                
                logger.info(f"Ollama generation successful. Response length: {len(generated_text)}")
                
                return {
                    "generated_text": generated_text,
                    "model_name": self.model_name,
                    "tokens_used": data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
                    "input_tokens": data.get("prompt_eval_count", 0),
                    "output_tokens": data.get("eval_count", 0),
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "status": "success"
                }
                
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Ollama: {str(e)}")
            raise Exception(
                "LLM request to Ollama failed: Cannot connect to Ollama server. "
                "Make sure Ollama is running (ollama serve)"
            )
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out: {str(e)}")
            raise Exception(
                f"LLM request to Ollama timed out after {self.timeout} seconds. "
                "Try reducing max_tokens or check Ollama server."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama returned error status: {e.response.status_code}")
            raise Exception(
                f"LLM request to Ollama failed: HTTP {e.response.status_code}. "
                f"Response: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise Exception(f"LLM request to Ollama failed: {str(e)}")
    
    async def generate_with_template(
        self,
        template: str,
        variables: Dict[str, Any],
        temperature: float = 0.7,
        max_tokens: int = 256,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using a prompt template.
        
        Args:
            template: Prompt template string with {variable} placeholders
            variables: Dict of variables to fill in the template
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters
        
        Returns:
            Dict with generated text and metadata
        """
        try:
            # Smart template rendering with intelligent value formatting
            rendered_prompt = template
            for key, value in variables.items():
                # Format value intelligently (handles lists, dicts, etc.)
                formatted_value = LLMService._format_template_value(value)
                # Replace all occurrences of {key} with formatted value
                rendered_prompt = rendered_prompt.replace(f"{{{key}}}", formatted_value)
            
            logger.debug(f"Rendered prompt: {rendered_prompt[:100]}...")
            
            # Generate text
            return await self.generate_text(
                prompt=rendered_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Template rendering or generation failed: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            import httpx
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Ollama connection"""
        return {
            "model_name": self.model_name,
            "ollama_url": self.ollama_url,
            "available": self.is_available(),
            "backend": "ollama"
        }
