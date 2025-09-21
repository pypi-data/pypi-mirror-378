"""
Tool Call API client for AgentRouter SDK
"""

import json
from typing import Any, Dict, List, Optional

from agentrouter.api.base import BaseAPIClient
from agentrouter.exceptions import APIError, ValidationError
from agentrouter.types import (
    APIResponse,
    Message,
    ToolDefinition,
    ToolChoice,
    ToolCall,
)
from agentrouter.validators.message_flow import MessageFlowValidator
from agentrouter.utils.logging import log_api_call, log_payload, log_response, get_logger


logger = get_logger(__name__)


class ToolCallAPIClient(BaseAPIClient):
    """
    Client for Tool Call API interactions
    """
    
    ENDPOINT = "/usf/v1/agent/tool-call"
    
    async def create_tool_calls(
        self,
        messages: List[Message],
        tools: List[ToolDefinition],
        tool_choice: ToolChoice,
        model: str = "usf-mini",
        provider: Optional[str] = None,
        introduction: Optional[str] = None,
        instruction: Optional[str] = None,
        knowledge_cutoff: Optional[str] = None,
        backstory: Optional[str] = None,
        goal: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> APIResponse:
        """
        Create tool calls using the Tool Call API
        
        Args:
            messages: Conversation messages
            tools: Available tools (required, non-empty)
            tool_choice: Tool choice specification (required)
            model: Model to use
            provider: Model provider
            introduction: Agent introduction
            instruction: Custom instruction for the agent
            knowledge_cutoff: Knowledge cutoff date
            backstory: Agent backstory
            goal: Agent goal
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            API response with tool calls
            
        Raises:
            ValidationError: If input validation fails
            APIError: If API call fails
        """
        # Validate messages for Tool Call API
        try:
            # Note: We're not passing last_plan_response here since we can't access it
            # from this method. The validation will check basic requirements.
            MessageFlowValidator.validate_for_tool_call_api(
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )
        except ValidationError as e:
            logger.error(f"Tool Call API validation failed: {str(e)}")
            raise
        
        # Additional validation
        if not tools:
            raise ValidationError("Tools cannot be empty for Tool Call API")
        
        if not tool_choice:
            raise ValidationError("Tool choice is required for Tool Call API")
        
        # Convert messages to dict format (handle both dict and Message objects)
        messages_dict = []
        for msg in messages:
            if isinstance(msg, dict):
                # Already a dictionary, just add it
                messages_dict.append(msg)
            else:
                # Convert Message object to dict
                msg_dict = {
                    "role": msg.role.value if hasattr(msg.role, 'value') else msg.role,
                    "content": msg.content,
                }
                if msg.name:
                    msg_dict["name"] = msg.name
                if msg.tool_calls:
                    msg_dict["tool_calls"] = msg.tool_calls
                if msg.tool_call_id:
                    msg_dict["tool_call_id"] = msg.tool_call_id
                # IMPORTANT: Preserve type field for Plan API messages
                if hasattr(msg, 'type'):
                    msg_dict["type"] = msg.type
                # IMPORTANT: Preserve tool_choice for Plan API messages
                if hasattr(msg, 'tool_choice'):
                    msg_dict["tool_choice"] = msg.tool_choice
                messages_dict.append(msg_dict)
        
        # Convert tools to dict format
        tools_dict = []
        for tool in tools:
            tools_dict.append({
                "type": tool.type,
                "function": {
                    "name": tool.function.name,
                    "description": tool.function.description,
                    "parameters": tool.function.parameters,
                }
            })
        
        # Convert tool choice to dict format
        tool_choice_dict = {
            "type": tool_choice.type.value if hasattr(tool_choice.type, 'value') else tool_choice.type,
        }
        if tool_choice.name:
            tool_choice_dict["name"] = tool_choice.name
        
        # Build payload
        payload = {
            "messages": messages_dict,
            "tools": tools_dict,
            "tool_choice": tool_choice_dict,
            "model": model,
        }
        
        # Add optional parameters
        if provider:
            payload["provider"] = provider
        if introduction is not None:
            payload["introduction"] = introduction
        if instruction is not None:
            payload["instruction"] = instruction
        if knowledge_cutoff is not None:
            payload["knowledge_cutoff"] = knowledge_cutoff
        if backstory is not None:
            payload["backstory"] = backstory
        if goal is not None:
            payload["goal"] = goal
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        # Log API call
        tool_choice_name = tool_choice.name or tool_choice.type
        log_api_call("Tool Call API", details={
            "messages": len(messages),
            "tools": len(tools),
            "choice": tool_choice_name
        })
        
        # Log payload in debug mode
        log_payload("Tool Call API Request", payload)
        
        try:
            response_data = await self.post(self.ENDPOINT, payload)
            
            # Parse and validate response
            response = APIResponse(**response_data)
            
            # Check for successful response
            if response.status != 1:
                raise APIError(
                    f"Tool Call API failed: {response.message}",
                    api_name="Tool Call API",
                    details={"response": response_data}
                )
            
            # Log successful response
            log_response("Tool Call API", "success", response_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create tool calls: {str(e)}")
            log_response("Tool Call API", "failed")
            if isinstance(e, (APIError, ValidationError)):
                raise
            raise APIError(
                f"Failed to create tool calls: {str(e)}",
                api_name="Tool Call API"
            ) from e
    
    def extract_tool_calls(self, response: APIResponse) -> List[ToolCall]:
        """
        Extract tool calls from Tool Call API response
        
        Args:
            response: API response from Tool Call API
            
        Returns:
            List of tool calls
        """
        tool_calls = []
        
        if not response.choices:
            return tool_calls
        
        message = response.choices[0].message
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                # Parse tool call
                if isinstance(tc, dict):
                    tool_call = ToolCall(**tc)
                else:
                    tool_call = tc
                tool_calls.append(tool_call)
        
        return tool_calls
    
    def format_tool_response(
        self,
        tool_call_id: str,
        tool_name: str,
        result: Any
    ) -> Message:
        """
        Format tool execution result as a message
        
        Args:
            tool_call_id: ID of the tool call
            tool_name: Name of the tool
            result: Tool execution result
            
        Returns:
            Formatted message with tool response
        """
        # Convert result to JSON string if needed
        if not isinstance(result, str):
            try:
                content = json.dumps(result, indent=2)
            except Exception:
                content = str(result)
        else:
            content = result
        
        return Message(
            role="tool",
            content=content,
            name=tool_name,
            tool_call_id=tool_call_id,
        )