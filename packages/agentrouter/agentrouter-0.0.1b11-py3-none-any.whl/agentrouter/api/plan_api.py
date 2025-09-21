"""
Plan API client for AgentRouter SDK
"""

from typing import Any, Dict, List, Optional

from agentrouter.api.base import BaseAPIClient
from agentrouter.exceptions import APIError, ValidationError
from agentrouter.types import (
    APIResponse,
    Message,
    ToolDefinition,
    AgentStatus,
    ToolChoice,
)
from agentrouter.validators.message_flow import MessageFlowValidator
from agentrouter.utils.logging import log_api_call, log_payload, log_response, get_logger


logger = get_logger(__name__)


class PlanAPIClient(BaseAPIClient):
    """
    Client for Plan API interactions
    """
    
    ENDPOINT = "/usf/v1/agent/plan"
    
    async def create_plan(
        self,
        messages: List[Message],
        model: str = "usf-mini",
        provider: Optional[str] = None,
        tools: Optional[List[ToolDefinition]] = None,
        introduction: Optional[str] = None,
        instruction: Optional[str] = None,
        knowledge_cutoff: Optional[str] = None,
        backstory: Optional[str] = None,
        goal: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> APIResponse:
        """
        Create a plan using the Plan API
        
        Args:
            messages: Conversation messages
            model: Model to use
            provider: Model provider
            tools: Available tools
            introduction: Agent introduction
            instruction: Custom instruction for the agent
            knowledge_cutoff: Knowledge cutoff date
            backstory: Agent backstory
            goal: Agent goal
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            API response with plan
            
        Raises:
            ValidationError: If input validation fails
            APIError: If API call fails
        """
        # Validate messages for Plan API
        try:
            MessageFlowValidator.validate_for_plan_api(messages)
        except ValidationError as e:
            logger.error(f"Plan API validation failed: {str(e)}")
            raise
        
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
                messages_dict.append(msg_dict)
        
        # Convert tools to dict format
        tools_dict = []
        if tools:
            for tool in tools:
                tools_dict.append({
                    "type": tool.type,
                    "function": {
                        "name": tool.function.name,
                        "description": tool.function.description,
                        "parameters": tool.function.parameters,
                    }
                })
        
        # Build payload
        payload = {
            "messages": messages_dict,
            "model": model,
        }
        
        # Add optional parameters
        if provider:
            payload["provider"] = provider
        if tools_dict:
            payload["tools"] = tools_dict
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
        log_api_call("Plan API", details={
            "messages": len(messages),
            "tools": len(tools_dict),
            "model": model
        })
        
        # Log payload in debug mode
        log_payload("Plan API Request", payload)
        
        try:
            response_data = await self.post(self.ENDPOINT, payload)
            
            # Parse and validate response
            response = APIResponse(**response_data)
            
            # Check for successful response
            if response.status != 1:
                raise APIError(
                    f"Plan API failed: {response.message}",
                    api_name="Plan API",
                    details={"response": response_data}
                )
            
            # Log successful response
            log_response("Plan API", "success", response_data)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create plan: {str(e)}")
            log_response("Plan API", "failed")
            if isinstance(e, (APIError, ValidationError)):
                raise
            raise APIError(
                f"Failed to create plan: {str(e)}",
                api_name="Plan API"
            ) from e
    
    def should_call_tool(self, response: APIResponse) -> bool:
        """
        Check if tool call is needed based on Plan API response
        
        Args:
            response: API response from Plan API
            
        Returns:
            True if tool call is needed, False otherwise
        """
        if not response.choices:
            return False
        
        message = response.choices[0].message
        
        # Check agent status
        if hasattr(message, 'agent_status'):
            if message.agent_status == AgentStatus.RUNNING:
                return True
            if message.agent_status == AgentStatus.PREPARING_FINAL_RESPONSE:
                return False
        
        # Check tool choice
        if hasattr(message, 'tool_choice') and message.tool_choice:
            return message.tool_choice.type != "none"
        
        return False
    
    def get_tool_choice(self, response: APIResponse) -> Optional[ToolChoice]:
        """
        Extract tool choice from Plan API response
        
        Args:
            response: API response from Plan API
            
        Returns:
            Tool choice if present, None otherwise
        """
        if not response.choices:
            return None
        
        message = response.choices[0].message
        
        if hasattr(message, 'tool_choice'):
            return message.tool_choice
        
        return None
    
    def get_agent_status(self, response: APIResponse) -> AgentStatus:
        """
        Get agent status from Plan API response
        
        Args:
            response: API response from Plan API
            
        Returns:
            Agent status
        """
        if not response.choices:
            return AgentStatus.IDLE
        
        message = response.choices[0].message
        
        if hasattr(message, 'agent_status'):
            return message.agent_status
        
        return AgentStatus.IDLE