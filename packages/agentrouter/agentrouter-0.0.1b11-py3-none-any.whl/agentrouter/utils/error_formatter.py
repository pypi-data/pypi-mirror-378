"""
Error formatting utilities for AgentRouter SDK
"""

import json
import logging
from copy import deepcopy
from typing import Optional, Dict, Any

from agentrouter.types import Message

logger = logging.getLogger(__name__)


class ErrorFormatter:
    """
    Formats errors consistently across the SDK while maintaining worker isolation
    """
    
    # Standard error templates - no internal details exposed
    DEFAULT_ERROR_TEMPLATE = "Error: {component} is not responding, don't have enough details to understand the error"
    WORKER_ERROR_TEMPLATE = "Error: Worker agent '{worker_name}' is not responding"
    WORKER_ERROR_WITH_MSG = "Error: Worker agent '{worker_name}' failed: {error_msg}"
    TOOL_ERROR_TEMPLATE = "Error: Tool '{tool_name}' is not responding"
    TOOL_ERROR_WITH_MSG = "Error: Tool '{tool_name}' failed: {error_msg}"
    
    # Standard error messages for different scenarios
    ERROR_MESSAGES = {
        "not_responding": "Error: {component} is not responding",
        "failed": "Error: {component} failed to complete the task",
        "timeout": "Error: {component} timed out",
        "not_found": "Error: {component} not found",
        "invalid_input": "Error: Invalid input for {component}",
        "network_error": "Error: Network error when calling {component}",
        "api_error": "Error: API error from {component}"
    }
    
    @staticmethod
    def format_tool_error(
        tool_name: str,
        tool_call_id: str,
        error: Optional[Exception] = None,
        include_details: bool = False
    ) -> Message:
        """
        Format tool execution error as message.
        
        Args:
            tool_name: Name of the tool
            tool_call_id: ID of the tool call
            error: Optional exception that occurred
            include_details: Whether to include error details (default: False for isolation)
            
        Returns:
            Formatted tool response message with error
        """
        # Determine error message
        if error and str(error) and include_details:
            # Only include details if explicitly requested (not for worker agents)
            error_content = {
                "error": str(error),
                "tool_name": tool_name,
                "status": "failed"
            }
        else:
            # Default safe error message - no internal details
            error_content = {
                "error": ErrorFormatter.TOOL_ERROR_TEMPLATE.format(tool_name=tool_name),
                "status": "failed"
            }
        
        return Message(
            role="tool",
            content=json.dumps(error_content),
            name=tool_name,
            tool_call_id=tool_call_id
        )
    
    @staticmethod
    def format_worker_error(
        worker_name: str,
        tool_call_id: str,
        error: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        Format worker execution error with complete isolation.
        No internal details are exposed.
        
        Args:
            worker_name: Name of the worker
            tool_call_id: ID of the tool call
            error: Optional exception that occurred (will not be exposed)
            
        Returns:
            Formatted error response with generic message
        """
        # Never expose internal worker errors
        error_msg = ErrorFormatter.WORKER_ERROR_TEMPLATE.format(worker_name=worker_name)
        
        # Log the actual error internally for debugging
        if error:
            logger.error(f"Worker '{worker_name}' internal error (not exposed): {str(error)}")
        
        return {
            "tool_call_id": tool_call_id,
            "tool_name": worker_name,
            "content": {
                "error": error_msg,
                "status": "failed"
            },
            "success": False
        }
    
    @staticmethod
    def ensure_tool_response(
        tool_call_id: str,
        tool_name: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        is_worker: bool = False
    ) -> Message:
        """
        Ensure a tool response is always generated, even on failure.
        
        Args:
            tool_call_id: ID of the tool call
            tool_name: Name of the tool
            result: Optional successful result
            error: Optional error that occurred
            is_worker: Whether this is a worker agent (affects error detail exposure)
            
        Returns:
            Tool response message
        """
        if result and result.get("success"):
            # Successful execution
            content = result.get("content", {})
            if not isinstance(content, str):
                content = json.dumps(content)
            
            return Message(
                role="tool",
                content=content,
                name=tool_name,
                tool_call_id=tool_call_id
            )
        else:
            # Failed execution or error
            if is_worker:
                # Worker agent - use generic error message
                error_msg = ErrorFormatter.WORKER_ERROR_TEMPLATE.format(worker_name=tool_name)
            else:
                # Regular tool - can include some details
                if error and str(error):
                    error_msg = ErrorFormatter.TOOL_ERROR_WITH_MSG.format(
                        tool_name=tool_name,
                        error_msg=str(error)
                    )
                else:
                    error_msg = ErrorFormatter.TOOL_ERROR_TEMPLATE.format(tool_name=tool_name)
            
            return Message(
                role="tool",
                content=json.dumps({"error": error_msg, "status": "failed"}),
                name=tool_name,
                tool_call_id=tool_call_id
            )
    
    @staticmethod
    def get_standard_error_message(
        component: str,
        error_type: str = "not_responding"
    ) -> str:
        """
        Get a standard error message for a component.
        
        Args:
            component: Component name
            error_type: Type of error from ERROR_MESSAGES
            
        Returns:
            Standard error message
        """
        template = ErrorFormatter.ERROR_MESSAGES.get(
            error_type,
            ErrorFormatter.DEFAULT_ERROR_TEMPLATE
        )
        return template.format(component=component)
    
    @staticmethod
    def format_api_error(
        api_name: str,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> str:
        """
        Format API error message.
        
        Args:
            api_name: Name of the API
            status_code: HTTP status code if available
            error_message: Error message if available
            
        Returns:
            Formatted error message
        """
        if status_code:
            if status_code == 429:
                return f"Error: {api_name} rate limit exceeded"
            elif status_code == 401:
                return f"Error: {api_name} authentication failed"
            elif status_code == 403:
                return f"Error: {api_name} authorization failed"
            elif status_code >= 500:
                return f"Error: {api_name} service unavailable"
            elif status_code >= 400:
                return f"Error: {api_name} request failed (HTTP {status_code})"
        
        if error_message:
            return f"Error: {api_name} failed: {error_message}"
        
        return f"Error: {api_name} is not responding"
    
    @staticmethod
    def create_error_tool_response(
        tool_call_id: str,
        tool_name: str,
        error_type: str = "not_responding"
    ) -> Message:
        """
        Create a standard error tool response.
        
        Args:
            tool_call_id: Tool call ID
            tool_name: Tool name
            error_type: Type of error
            
        Returns:
            Error tool response message
        """
        error_msg = ErrorFormatter.get_standard_error_message(tool_name, error_type)
        
        return Message(
            role="tool",
            content=json.dumps({
                "error": error_msg,
                "status": "failed",
                "error_type": error_type
            }),
            name=tool_name,
            tool_call_id=tool_call_id
        )


class IsolatedWorkerErrorHandler:
    """
    Handles worker errors while maintaining complete isolation.
    No internal details are ever exposed to parent agents.
    """
    
    @staticmethod
    async def execute_worker_isolated(
        worker: Any,  # WorkerAgent type
        tool_call: Any,  # ToolCall type
        parent_messages: list,
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Execute worker with complete isolation.
        
        Parent receives ONLY:
        - Success: Final response content (string only)
        - Failure: Generic error message (no internal details)
        
        Args:
            worker: Worker agent to execute
            tool_call: Tool call containing task (and optional context)
            parent_messages: Parent messages (if access allowed)
            timeout: Execution timeout in seconds (configurable: 5-300)
            
        Returns:
            Isolated result with no internal details
        """
        import asyncio
        import json
        
        worker_name = worker.name
        tool_call_id = tool_call.id
        
        try:
            # Parse task from tool call
            if isinstance(tool_call.function, dict):
                arguments_str = tool_call.function.get("arguments", "{}")
            else:
                arguments_str = getattr(tool_call.function, "arguments", "{}")
            
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                arguments = {}

            task = arguments.get("task", "")
            context = arguments.get("context", "")

            # Prepare isolated messages for worker
            from agentrouter.types import Message
            worker_messages = []

            # Only pass history if explicitly configured. Deep copy to keep parent state isolated.
            if hasattr(worker, 'config') and worker.config.access_parent_history:
                worker_messages = deepcopy(parent_messages)
                if worker.config.trim_last_parent_user_message and worker_messages:
                    # Remove last user message from copied history when requested.
                    for i in range(len(worker_messages) - 1, -1, -1):
                        msg_role = worker_messages[i].role
                        if hasattr(msg_role, 'value'):
                            msg_role = msg_role.value
                        if msg_role == "user":
                            worker_messages.pop(i)
                            break

            # Add task as new user message (context stays isolated in the system message).
            task_message = Message(
                role="user",
                content=str(task)
            )
            worker_messages.append(task_message)
            additional_sections = [f"### Context: {str(context)}"] if context else None
            worker_messages = worker._update_or_add_system_message(
                worker_messages,
                additional_sections=additional_sections
            )

            # Execute worker with timeout - internal details stay within worker
            result = await asyncio.wait_for(
                worker.execute(worker_messages),
                timeout=timeout
            )
            
            # Extract ONLY the final response content - no internal details
            if isinstance(result, dict) and "choices" in result and result["choices"]:
                content = result["choices"][0].get("message", {}).get("content")
                if not content:
                    # No content in response - this is an error
                    raise ValueError("No content in worker response")
            else:
                # Invalid response format - this is an error
                raise ValueError("Invalid response format from worker")
            
            # Return clean response - direct final answer only, no internal execution details
            return {
                "tool_call_id": tool_call_id,
                "tool_name": worker_name,
                "content": str(content),
                "success": True
            }
            
        except asyncio.TimeoutError:
            # Worker timed out - return generic error
            logger.error(f"Worker '{worker_name}' timed out after {timeout}s (internal)")
            
            return {
                "tool_call_id": tool_call_id,
                "tool_name": worker_name,
                "content": {
                    "error": ErrorFormatter.WORKER_ERROR_TEMPLATE.format(worker_name=worker_name),
                    "timeout_seconds": timeout
                },
                "success": False
            }
            
        except Exception as e:
            # Worker failed - log internally but return generic error
            logger.error(f"Worker '{worker_name}' internal error: {str(e)}", exc_info=True)
            
            # Never expose internal error details
            return {
                "tool_call_id": tool_call_id,
                "tool_name": worker_name,
                "content": {
                    "error": ErrorFormatter.WORKER_ERROR_TEMPLATE.format(worker_name=worker_name)
                },
                "success": False
            }
