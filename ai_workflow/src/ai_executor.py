"""
AI Prompt Executor Module
Handles execution of AI prompts using OpenAI or compatible APIs
"""

import os
import logging
from typing import Dict, List, Optional, Any
import json

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


class AIPromptExecutor:
    """Executor for running AI prompts using OpenAI or compatible APIs."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize AI prompt executor.
        
        Args:
            api_key: OpenAI API key. If not provided, reads from OPENAI_API_KEY env var.
            model: The model to use (default: gpt-3.5-turbo)
        """
        if OpenAI is None:
            raise ImportError(
                "openai is not installed. "
                "Install it with: pip install openai"
            )
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        logger.info(f"AI Prompt Executor initialized with model: {model}")
    
    def execute_prompt(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a single AI prompt.
        
        Args:
            prompt: The prompt to execute
            system_message: Optional system message to set context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters for the API
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            messages = []
            
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            api_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                api_params["max_tokens"] = max_tokens
            
            api_params.update(kwargs)
            
            logger.info(f"Executing prompt with model {self.model}")
            response = self.client.chat.completions.create(**api_params)
            
            result = {
                "success": True,
                "response": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"Prompt executed successfully. Tokens used: {result['usage']['total_tokens']}")
            return result
        
        except Exception as e:
            logger.error(f"Error executing prompt: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def execute_batch_prompts(
        self,
        prompts: List[Dict[str, Any]],
        system_message: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple prompts in batch.
        
        Args:
            prompts: List of prompt configurations
            system_message: Optional system message for all prompts
            
        Returns:
            List of results for each prompt
        """
        results = []
        
        for i, prompt_config in enumerate(prompts):
            logger.info(f"Executing prompt {i+1}/{len(prompts)}")
            
            prompt = prompt_config.get("prompt", "")
            temp = prompt_config.get("temperature", 0.7)
            max_tok = prompt_config.get("max_tokens")
            
            result = self.execute_prompt(
                prompt=prompt,
                system_message=system_message,
                temperature=temp,
                max_tokens=max_tok
            )
            
            result["prompt_id"] = prompt_config.get("id", i)
            results.append(result)
        
        logger.info(f"Batch execution completed. {len(results)} prompts processed")
        return results
    
    def execute_with_context(
        self,
        prompt: str,
        context: Dict[str, Any],
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a prompt with additional context data.
        
        Args:
            prompt: The prompt template
            context: Context variables to inject into prompt
            system_message: Optional system message
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Replace context variables in prompt
        formatted_prompt = prompt
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            if placeholder in formatted_prompt:
                formatted_prompt = formatted_prompt.replace(placeholder, str(value))
        
        logger.info(f"Executing prompt with {len(context)} context variables")
        return self.execute_prompt(
            prompt=formatted_prompt,
            system_message=system_message
        )
    
    def validate_api_connection(self) -> bool:
        """
        Validate that API connection is working.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_result = self.execute_prompt(
                prompt="Say 'Hello' if you can read this.",
                max_tokens=10
            )
            return test_result.get("success", False)
        except Exception as e:
            logger.error(f"API validation failed: {str(e)}")
            return False
