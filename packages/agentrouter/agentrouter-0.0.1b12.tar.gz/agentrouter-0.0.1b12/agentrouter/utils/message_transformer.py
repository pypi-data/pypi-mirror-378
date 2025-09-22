"""
Message transformation utilities for AgentRouter SDK
"""

import logging
from copy import deepcopy
from typing import List, Optional, Dict, Any

from agentrouter.types import Message, APIResponse
from agentrouter.utils.logging import is_debug_mode

logger = logging.getLogger(__name__)


class MessageTransformer:
    """
    Transforms messages for final response generation and API calls
    """
    
    @staticmethod
    def prepare_for_final_response(
        messages: List[Message],
        last_plan_response: Optional[APIResponse] = None
    ) -> List[Message]:
        """
        Prepare messages for final response generation.
        
        Steps:
        1. Remove all plan messages except the last one
        2. Transform last plan message role from 'assistant' to 'user'
        3. Keep all tool calls and tool responses intact
        4. Ensure proper message ordering
        
        Args:
            messages: Current message list
            last_plan_response: Optional last plan API response
            
        Returns:
            Transformed messages ready for final response
        """
        if not messages:
            return []  # Return empty list instead of None/original (which could be None)
        
        transformed = []
        plan_messages = []
        
        # Process messages - separate plan messages from others
        for msg in messages:
            # Handle both Message objects and dictionaries
            if isinstance(msg, dict):
                # Convert dict to Message object
                msg_copy = Message(**msg)
            else:
                # Create a deep copy to avoid modifying original
                msg_copy = deepcopy(msg)
            
            # Check if it's a plan message
            is_plan_message = (
                (hasattr(msg_copy, 'type') and msg_copy.type == 'agent_plan') or
                (isinstance(msg_copy, dict) and msg_copy.get('type') == 'agent_plan')
            )
            
            if is_plan_message:
                plan_messages.append(msg_copy)
            else:
                # Keep all non-plan messages (user, assistant, tool)
                transformed.append(msg_copy)
        
        # Add only the last plan message and transform its role
        if plan_messages:
            last_plan = plan_messages[-1]
            
            # Transform role from 'assistant' to 'user' for final response
            last_plan.role = "user"
            
            # Remove the type attribute to clean the message
            if hasattr(last_plan, 'type'):
                delattr(last_plan, 'type')
            
            # Remove plan-specific attributes
            for attr in ['plan', 'reasoning', 'final_decision', 'agent_status', 'tool_choice']:
                if hasattr(last_plan, attr):
                    delattr(last_plan, attr)
            
            transformed.append(last_plan)
        
        # Validate the final message structure
        if transformed:
            last_msg = transformed[-1]
            # Handle different role formats
            if hasattr(last_msg, 'role'):
                last_role = last_msg.role.value if hasattr(last_msg.role, 'value') else last_msg.role
            elif isinstance(last_msg, dict):
                last_role = last_msg.get('role', '')
            else:
                last_role = ''
            
            if last_role != "user":
                logger.warning(
                    f"Last message role is '{last_role}', expected 'user' for final response. "
                    "This may cause issues with the OpenAI API."
                )
        
        logger.debug(f"Transformed {len(messages)} messages to {len(transformed)} for final response")
        
        return transformed

    @staticmethod
    def prepare_forced_final_messages(messages: List[Message]) -> List[Message]:
        """Clean up message history when a forced final response is required."""
        if not messages:
            return []

        # Work on isolated copies so we never mutate the original history
        prepared: List[Message] = []
        for msg in messages:
            if isinstance(msg, dict):
                prepared.append(Message(**msg))
            else:
                prepared.append(deepcopy(msg))

        # Drop the trailing plan message if it still recommends tool usage
        if prepared:
            last_msg = prepared[-1]
            if (
                getattr(last_msg, "type", None) == "agent_plan"
                and getattr(last_msg, "tool_choice", None)
            ):
                if is_debug_mode():
                    logger.debug("Removing last plan message that suggests additional tool calls")
                prepared.pop()

        retained_plan: Optional[Message] = None
        if prepared:
            last_msg = prepared[-1]
            last_role = getattr(last_msg, "role", None)
            if hasattr(last_role, "value"):
                last_role = last_role.value
            if last_role == "assistant" and getattr(last_msg, "type", None) == "agent_plan":
                plan_payload = last_msg.model_dump()
                # Convert to final-user framing and strip agent-only metadata
                plan_payload["role"] = "user"
                plan_payload.pop("type", None)
                plan_payload.pop("tool_choice", None)
                plan_payload.pop("agent_status", None)
                retained_plan = Message(**plan_payload)

        cleaned: List[Message] = [
            msg for msg in prepared
            if getattr(msg, "type", None) != "agent_plan"
        ]

        if retained_plan is not None:
            cleaned.append(retained_plan)

        return cleaned

    @staticmethod
    def clean_messages_for_api(messages: List[Message]) -> List[Dict[str, Any]]:
        """
        Clean messages for API consumption (OpenAI format).
        
        Args:
            messages: Messages to clean
            
        Returns:
            List of cleaned message dictionaries
        """
        cleaned = []
        
        for msg in messages:
            # Handle both Message objects and dictionaries
            if isinstance(msg, dict):
                role = msg.get('role', 'assistant')
                content = msg.get('content', '')
            else:
                # Get role value
                role = msg.role.value if hasattr(msg.role, 'value') else msg.role
                content = msg.content if hasattr(msg, 'content') else ''
            
            # Build basic message dict
            msg_dict = {
                "role": role,
                "content": content or ""
            }
            
            # Add optional fields if present
            if hasattr(msg, 'name') and msg.name:
                msg_dict["name"] = msg.name
            
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            
            if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            
            # Include type field for agent_plan messages (required for Tool Call API)
            if hasattr(msg, 'type') and msg.type in ['agent_plan', 'agent_tool_calls']:
                msg_dict["type"] = msg.type
            
            # Don't include other agent-specific attributes
            # (plan, reasoning, final_decision, agent_status, etc.)
            
            cleaned.append(msg_dict)
        
        return cleaned
    
    @staticmethod
    def remove_planning_messages(
        messages: List[Message],
        keep_last: bool = True
    ) -> List[Message]:
        """
        Remove planning messages from the message list.
        
        Args:
            messages: List of messages
            keep_last: Whether to keep the last planning message
            
        Returns:
            Messages with planning messages removed/filtered
        """
        if not messages:
            return []  # Return empty list instead of None/original (which could be None)
        
        filtered = []
        plan_messages = []
        
        for msg in messages:
            msg_copy = deepcopy(msg)
            
            if hasattr(msg_copy, 'type') and msg_copy.type == 'agent_plan':
                plan_messages.append(msg_copy)
            else:
                filtered.append(msg_copy)
        
        # Add last plan message if requested
        if keep_last and plan_messages:
            filtered.append(plan_messages[-1])
        
        return filtered
    
    @staticmethod
    def extract_tool_responses(messages: List[Message]) -> List[Message]:
        """
        Extract only tool response messages.
        
        Args:
            messages: List of messages
            
        Returns:
            List of tool response messages only
        """
        tool_responses = []
        
        for msg in messages:
            # Handle both Message objects and dictionaries
            if isinstance(msg, dict):
                msg_role = msg.get('role', '')
            else:
                msg_role = msg.role.value if hasattr(msg.role, 'value') else msg.role
            
            if msg_role == "tool":
                if isinstance(msg, dict):
                    tool_responses.append(Message(**msg))
                else:
                    tool_responses.append(deepcopy(msg))
        
        return tool_responses
    
    @staticmethod
    def ensure_user_message_last(messages: List[Message]) -> List[Message]:
        """
        Ensure the last message is a user message.
        If not, transform or add appropriate message.
        
        Args:
            messages: List of messages
            
        Returns:
            Messages with user message last
        """
        if not messages:
            return []  # Return empty list instead of None/original (which could be None)
        
        # Handle both Message objects and dictionaries
        messages_copy = []
        for msg in messages:
            if isinstance(msg, dict):
                messages_copy.append(Message(**msg))
            else:
                messages_copy.append(deepcopy(msg))
        
        last_msg = messages_copy[-1]
        if isinstance(last_msg, dict):
            last_role = last_msg.get('role', '')
        else:
            last_role = last_msg.role.value if hasattr(last_msg.role, 'value') else last_msg.role
        
        if last_role == "user":
            return messages_copy
        
        # If last message is assistant with plan type, transform it
        if last_role == "assistant" and hasattr(last_msg, 'type') and last_msg.type == 'agent_plan':
            last_msg.role = "user"
            # Clean up plan-specific attributes
            for attr in ['type', 'plan', 'reasoning', 'final_decision', 'agent_status', 'tool_choice']:
                if hasattr(last_msg, attr):
                    delattr(last_msg, attr)
            return messages_copy
        
        # If last message is tool response, we might need to add a user message
        if last_role == "tool":
            # Check if there's a previous plan message we can use
            for i in range(len(messages_copy) - 2, -1, -1):
                msg = messages_copy[i]
                if hasattr(msg, 'type') and msg.type == 'agent_plan':
                    # Found a plan message - use its content as user message
                    user_msg = Message(
                        role="user",
                        content=msg.content or "Please provide the final response based on the tool results."
                    )
                    messages_copy.append(user_msg)
                    return messages_copy
            
            # No plan message found - add generic user message
            user_msg = Message(
                role="user",
                content="Please provide the final response based on the tool results."
            )
            messages_copy.append(user_msg)
        
        return messages_copy
    
    @staticmethod
    def convert_to_openai_format(messages: List[Message]) -> List[Dict[str, Any]]:
        """
        Convert messages to OpenAI API format.
        
        Args:
            messages: List of Message objects
            
        Returns:
            List of dictionaries in OpenAI format
        """
        openai_messages = []
        
        for msg in messages:
            # Get role string
            role = msg.role.value if hasattr(msg.role, 'value') else str(msg.role)
            
            # Build message dict
            msg_dict = {
                "role": role,
                "content": msg.content or ""
            }
            
            # Add type field for agent messages (needed for Tool Call API)
            if hasattr(msg, 'type') and msg.type in ['agent_plan', 'agent_tool_calls']:
                msg_dict["type"] = msg.type
            
            # Add name for tool messages
            if role == "tool" and hasattr(msg, 'name') and msg.name:
                msg_dict["name"] = msg.name
            
            # Add tool_call_id for tool responses
            if role == "tool" and hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                msg_dict["tool_call_id"] = msg.tool_call_id
            
            # Add tool_calls for assistant messages
            if role == "assistant" and hasattr(msg, 'tool_calls') and msg.tool_calls:
                msg_dict["tool_calls"] = msg.tool_calls
            
            openai_messages.append(msg_dict)
        
        return openai_messages
    
    @staticmethod
    def validate_and_fix_sequence(messages: List[Message]) -> List[Message]:
        """
        Validate and fix message sequence for API compatibility.
        
        Args:
            messages: List of messages
            
        Returns:
            Fixed message sequence
        """
        if not messages:
            return []  # Return empty list instead of None/original (which could be None)
        
        fixed = []
        prev_role = None
        
        for msg in messages:
            msg_copy = deepcopy(msg)
            curr_role = msg_copy.role.value if hasattr(msg_copy.role, 'value') else msg_copy.role
            
            # Check for duplicate consecutive roles (except tool responses)
            if prev_role == curr_role and curr_role != "tool":
                # Merge content if same role
                if fixed and fixed[-1].role == curr_role:
                    fixed[-1].content += "\n\n" + (msg_copy.content or "")
                    logger.debug(f"Merged consecutive {curr_role} messages")
                    continue
            
            fixed.append(msg_copy)
            prev_role = curr_role
        
        return fixed
