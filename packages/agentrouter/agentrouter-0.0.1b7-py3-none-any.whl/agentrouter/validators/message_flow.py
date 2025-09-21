"""
Message flow validation for AgentRouter SDK
"""

import logging
from typing import List, Optional, Any

from agentrouter.types import Message, APIResponse, ToolDefinition, ToolChoice
from agentrouter.exceptions import ValidationError

logger = logging.getLogger(__name__)


class MessageFlowValidator:
    """
    Validates message sequences for API calls to ensure proper flow control
    """
    
    @staticmethod
    def validate_for_plan_api(messages: List[Message]) -> None:
        """
        Validate messages before Plan API call.
        
        Rules:
        - Messages cannot be empty
        - Last message cannot be from plan agent (type: agent_plan)
        - Messages must have valid structure
        
        Args:
            messages: List of messages to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not messages:
            raise ValidationError("Messages cannot be empty for Plan API")
        
        # Check if last message is from plan agent
        last_message = messages[-1]
        
        # Get message type (handle both dict and Message objects)
        msg_type = None
        if isinstance(last_message, dict):
            msg_type = last_message.get('type')
        elif hasattr(last_message, 'type'):
            msg_type = last_message.type
            
        # Check for plan agent message type
        if msg_type == 'agent_plan':
            raise ValidationError(
                "Cannot call Plan API: Last message is from plan agent. "
                "A tool response or user message is required before calling Plan API again.",
                field="messages",
                details={"last_message_type": msg_type}
            )
        
        # Additional validation: Check for consecutive plan messages
        for i in range(len(messages) - 1):
            curr_msg = messages[i]
            next_msg = messages[i + 1]
            
            # Get message types (handle both dict and Message objects)
            curr_type = curr_msg.get('type') if isinstance(curr_msg, dict) else getattr(curr_msg, 'type', None)
            next_type = next_msg.get('type') if isinstance(next_msg, dict) else getattr(next_msg, 'type', None)
            
            # Check for consecutive plan messages without tool response
            if curr_type == 'agent_plan' and next_type == 'agent_plan':
                raise ValidationError(
                    "Invalid message sequence: Consecutive plan messages found without tool response",
                    field="messages",
                    details={"position": i}
                )
        
        logger.debug(f"Validated {len(messages)} messages for Plan API")
    
    @staticmethod
    def validate_for_tool_call_api(
        messages: List[Message],
        last_plan_response: Optional[APIResponse] = None,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[ToolChoice] = None
    ) -> None:
        """
        Validate messages before Tool Call API.
        
        Rules:
        - Messages cannot be empty
        - Last message must be from Plan API (type: agent_plan)
        - Plan must indicate tool call is needed (agent_status: running)
        - Requested tool must exist in tools list (if tool_choice specified)
        
        Args:
            messages: List of messages to validate
            last_plan_response: Last response from Plan API
            tools: Available tools
            tool_choice: Tool choice from Plan API
            
        Raises:
            ValidationError: If validation fails
        """
        if not messages:
            raise ValidationError("Messages cannot be empty for Tool Call API")
        
        # Check last message is from Plan API (handle both dict and Message objects)
        last_message = messages[-1]
        msg_type = last_message.get('type') if isinstance(last_message, dict) else getattr(last_message, 'type', None)
        
        if msg_type != 'agent_plan':
            raise ValidationError(
                "Cannot call Tool Call API: Last message must be from Plan API",
                field="messages",
                details={"last_message_type": msg_type or 'unknown'}
            )
        
        # Verify Plan API response indicates tool call is needed
        if last_plan_response:
            if hasattr(last_plan_response, 'choices') and last_plan_response.choices:
                choice = last_plan_response.choices[0]
                if hasattr(choice, 'message'):
                    message = choice.message
                    
                    # Check agent status
                    if hasattr(message, 'agent_status'):
                        if message.agent_status == 'preparing_final_response':
                            raise ValidationError(
                                "Cannot call Tool Call API: Plan indicates preparing final response",
                                field="agent_status",
                                details={"agent_status": message.agent_status}
                            )
                    
                    # Check tool_choice is present
                    if not hasattr(message, 'tool_choice') or not message.tool_choice:
                        raise ValidationError(
                            "Cannot call Tool Call API: Plan response does not indicate tool call needed",
                            field="tool_choice",
                            details={"has_tool_choice": False}
                        )
        
        # Validate tool exists if tool_choice specified
        if tool_choice and tools:
            if hasattr(tool_choice, 'name') and tool_choice.name:
                tool_names = [t.function.name for t in tools if hasattr(t, 'function')]
                if tool_choice.name not in tool_names:
                    raise ValidationError(
                        f"Tool '{tool_choice.name}' not found in available tools",
                        field="tool_choice",
                        details={
                            "requested_tool": tool_choice.name,
                            "available_tools": tool_names
                        }
                    )
        
        logger.debug(f"Validated messages for Tool Call API with tool_choice: {tool_choice}")
    
    @staticmethod
    def validate_tool_response(
        tool_response: Message,
        tool_call_id: str
    ) -> None:
        """
        Validate tool response message.
        
        Rules:
        - Role must be "tool"
        - Must have tool_call_id matching the request
        - Content must be present (even if error)
        
        Args:
            tool_response: Tool response message to validate
            tool_call_id: Expected tool call ID
            
        Raises:
            ValidationError: If validation fails
        """
        # Check role
        if tool_response.role != "tool":
            raise ValidationError(
                f"Tool response must have role 'tool', got '{tool_response.role}'",
                field="role",
                value=tool_response.role
            )
        
        # Check tool_call_id
        if not tool_response.tool_call_id:
            raise ValidationError(
                "Tool response must have tool_call_id",
                field="tool_call_id"
            )
        
        if tool_response.tool_call_id != tool_call_id:
            raise ValidationError(
                f"Tool response tool_call_id mismatch",
                field="tool_call_id",
                details={
                    "expected": tool_call_id,
                    "actual": tool_response.tool_call_id
                }
            )
        
        # Check content
        if tool_response.content is None:
            raise ValidationError(
                "Tool response must have content (even if error)",
                field="content"
            )
        
        logger.debug(f"Validated tool response for call_id: {tool_call_id}")
    
    @staticmethod
    def validate_for_final_response(messages: List[Message]) -> None:
        """
        Validate messages before final response generation.
        
        Rules:
        - Messages cannot be empty
        - Must have at least one user message
        - Last message should be appropriate for final response
        
        Args:
            messages: List of messages to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not messages:
            raise ValidationError("Messages cannot be empty for final response")
        
        # Check for at least one user message
        has_user_message = any(
            msg.role == "user" or 
            (hasattr(msg, 'role') and msg.role.value == "user" if hasattr(msg.role, 'value') else False)
            for msg in messages
        )
        
        if not has_user_message:
            raise ValidationError(
                "At least one user message required for final response",
                field="messages",
                details={"message_count": len(messages)}
            )
        
        # Check last message is appropriate (should be user after transformation)
        last_message = messages[-1]
        last_role = last_message.role.value if hasattr(last_message.role, 'value') else last_message.role
        
        if last_role not in ["user", "tool"]:
            logger.warning(
                f"Last message role '{last_role}' may not be appropriate for final response. "
                "Consider transforming to 'user' role."
            )
        
        logger.debug(f"Validated {len(messages)} messages for final response")
    
    @staticmethod
    def validate_message_sequence(messages: List[Message]) -> None:
        """
        Validate overall message sequence integrity.
        
        Rules:
        - No orphaned tool responses (tool response without preceding tool call)
        - No duplicate tool_call_ids
        - Proper role alternation where expected
        
        Args:
            messages: List of messages to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not messages:
            return
        
        tool_call_ids_seen = set()
        tool_calls_pending = {}
        
        for i, msg in enumerate(messages):
            msg_role = msg.role.value if hasattr(msg.role, 'value') else msg.role
            
            # Track tool calls
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if isinstance(tool_call, dict):
                        call_id = tool_call.get('id')
                        if call_id:
                            if call_id in tool_call_ids_seen:
                                raise ValidationError(
                                    f"Duplicate tool_call_id '{call_id}' found",
                                    field="tool_calls",
                                    details={"position": i, "duplicate_id": call_id}
                                )
                            tool_call_ids_seen.add(call_id)
                            tool_calls_pending[call_id] = i
            
            # Validate tool responses
            if msg_role == "tool":
                if not msg.tool_call_id:
                    raise ValidationError(
                        f"Tool response at position {i} missing tool_call_id",
                        field="tool_call_id",
                        details={"position": i}
                    )
                
                if msg.tool_call_id not in tool_calls_pending:
                    raise ValidationError(
                        f"Orphaned tool response: No preceding tool call for id '{msg.tool_call_id}'",
                        field="tool_call_id",
                        details={"position": i, "orphaned_id": msg.tool_call_id}
                    )
                
                # Remove from pending
                del tool_calls_pending[msg.tool_call_id]
        
        # Check for unanswered tool calls
        if tool_calls_pending:
            raise ValidationError(
                f"Unanswered tool calls found",
                field="tool_calls",
                details={"pending_ids": list(tool_calls_pending.keys())}
            )
        
        logger.debug(f"Message sequence validation passed for {len(messages)} messages")