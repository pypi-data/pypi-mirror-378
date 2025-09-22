"""
OpenAI SDK integration for final response generation
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, AsyncIterator

from agentrouter.types import Message
from agentrouter.utils.message_transformer import MessageTransformer
from agentrouter.exceptions import APIError, ConfigurationError

logger = logging.getLogger(__name__)

# Import OpenAI SDK conditionally
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not installed. Install with: pip install openai")


class OpenAIResponseGenerator:
    """
    Generates final responses using OpenAI SDK or compatible APIs
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        max_retries: int = 3
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: API key for authentication
            model: Model to use for generation
            base_url: Optional custom base URL for API
            organization: Optional organization ID
            max_retries: Maximum number of retries on failure
        """
        if not OPENAI_AVAILABLE:
            raise ConfigurationError(
                "OpenAI SDK is not installed. Install with: pip install openai"
            )
        
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.max_retries = max_retries
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            organization=organization,
            max_retries=max_retries
        )
        
        logger.info(
            f"Initialized OpenAI client with model '{model}'" +
            (f" and base URL '{base_url}'" if base_url else "")
        )
    
    async def generate_final_response(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        stop: Optional[List[str]] = None,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate final response using OpenAI SDK.
        
        Args:
            messages: Prepared messages for final response
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            streaming: Whether to stream the response
            presence_penalty: Presence penalty (-2 to 2)
            frequency_penalty: Frequency penalty (-2 to 2)
            stop: Stop sequences
            user: Unique user identifier
            
        Returns:
            OpenAI-formatted response
            
        Raises:
            APIError: If OpenAI API call fails
        """
        # Transform messages to OpenAI format
        openai_messages = MessageTransformer.convert_to_openai_format(messages)
        
        if not openai_messages:
            raise APIError("No messages to send to OpenAI API")
        
        # Validate last message is user
        if openai_messages[-1]["role"] != "user":
            logger.warning(
                f"Last message role is '{openai_messages[-1]['role']}', "
                "transforming to 'user' for OpenAI API"
            )
            # Transform last message to user if needed
            openai_messages[-1]["role"] = "user"
        
        try:
            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
                "presence_penalty": presence_penalty,
                "frequency_penalty": frequency_penalty,
                "stream": streaming
            }
            
            # Add optional parameters
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            if stop:
                request_params["stop"] = stop
            if user:
                request_params["user"] = user
            
            # Call OpenAI API
            logger.debug(f"Calling OpenAI API with {len(openai_messages)} messages")
            response = await self.client.chat.completions.create(**request_params)
            
            if streaming:
                # Handle streaming response
                return await self._handle_streaming_response(response)
            else:
                # Convert to expected format
                return self._format_response(response)
                
        except Exception as e:
            # Handle OpenAI API errors
            error_msg = str(e)
            
            # Check for specific error types
            if "rate_limit" in error_msg.lower():
                raise APIError(
                    "OpenAI API rate limit exceeded",
                    status_code=429,
                    api_name="OpenAI"
                ) from e
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                raise APIError(
                    "OpenAI API authentication failed",
                    status_code=401,
                    api_name="OpenAI"
                ) from e
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                raise APIError(
                    f"Model '{self.model}' not found",
                    status_code=404,
                    api_name="OpenAI"
                ) from e
            else:
                raise APIError(
                    f"OpenAI API error: {error_msg}",
                    api_name="OpenAI"
                ) from e
    
    def _format_response(self, response: Any) -> Dict[str, Any]:
        """
        Format OpenAI response to expected structure.
        
        Args:
            response: OpenAI API response
            
        Returns:
            Formatted response dictionary
        """
        return {
            "id": response.id,
            "object": response.object,
            "created": response.created,
            "model": response.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content
                    },
                    "finish_reason": choice.finish_reason
                }
                for choice in response.choices
            ],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            } if response.usage else {}
        }
    
    async def _handle_streaming_response(
        self,
        stream: AsyncIterator
    ) -> Dict[str, Any]:
        """
        Handle streaming response from OpenAI.
        
        Args:
            stream: Streaming response iterator
            
        Returns:
            Accumulated response dictionary
        """
        accumulated_content = ""
        response_data = None
        finish_reason = None
        
        try:
            async for chunk in stream:
                # Extract content from chunk
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    
                    if delta and delta.content:
                        accumulated_content += delta.content
                    
                    # Check for finish reason
                    if chunk.choices[0].finish_reason:
                        finish_reason = chunk.choices[0].finish_reason
                
                # Store metadata from first chunk
                if not response_data:
                    response_data = {
                        "id": chunk.id,
                        "object": chunk.object,
                        "created": chunk.created,
                        "model": chunk.model
                    }
            
            # Return accumulated response
            return {
                **response_data,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": accumulated_content
                    },
                    "finish_reason": finish_reason or "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,  # Not available in streaming
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error handling streaming response: {str(e)}")
            raise APIError(
                f"Failed to handle streaming response: {str(e)}",
                api_name="OpenAI"
            ) from e
    


class MockOpenAIGenerator:
    """
    Mock OpenAI generator for testing without API calls
    """
    
    def __init__(self, model: str = "mock-model"):
        """Initialize mock generator"""
        self.model = model
        logger.info("Using MockOpenAIGenerator for testing")
    
    async def generate_final_response(
        self,
        messages: List[Message],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate mock response for testing.
        
        Args:
            messages: Input messages
            **kwargs: Additional parameters (ignored)
            
        Returns:
            Mock response in OpenAI format
        """
        # Extract last user message
        last_user_msg = ""
        for msg in reversed(messages):
            msg_role = msg.role.value if hasattr(msg.role, 'value') else msg.role
            if msg_role == "user":
                last_user_msg = msg.content
                break
        
        # Generate mock response
        mock_content = f"Mock response to: {last_user_msg[:50]}..."
        
        return {
            "id": "mock-" + str(int(asyncio.get_event_loop().time())),
            "object": "chat.completion",
            "created": int(asyncio.get_event_loop().time()),
            "model": self.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": mock_content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": sum(len(m.content or "") for m in messages),
                "completion_tokens": len(mock_content),
                "total_tokens": sum(len(m.content or "") for m in messages) + len(mock_content)
            }
        }