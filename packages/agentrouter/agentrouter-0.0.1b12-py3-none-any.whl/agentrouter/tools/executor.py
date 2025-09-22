"""
Tool executor for running registered tools
"""

import asyncio
import inspect
import json
from typing import Any, Callable, Dict, List, Optional, Union

from agentrouter.exceptions import ToolError, ValidationError
from agentrouter.types import RegisteredTool, ToolCall, Message
from agentrouter.tools.registry import ToolRegistry
from agentrouter.utils.error_formatter import ErrorFormatter
from agentrouter.utils.logging import log_tool_execution, get_logger


logger = get_logger(__name__)


class ToolExecutor:
    """
    Executor for running tools
    """
    
    def __init__(self, registry: ToolRegistry):
        """
        Initialize tool executor
        
        Args:
            registry: Tool registry containing tools to execute
        """
        self.registry = registry
        self._execution_count = 0
        self._execution_history: List[Dict[str, Any]] = []
        
        logger.debug(f"Created tool executor with registry: {registry.name}")
    
    async def execute(
        self,
        tool_call: ToolCall,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool call
        
        Args:
            tool_call: Tool call to execute
            context: Optional execution context
            
        Returns:
            Tool execution result
            
        Raises:
            ToolError: If tool execution fails
        """
        tool_name = tool_call.function.get("name")
        if not tool_name:
            raise ToolError("Tool call missing function name")
        
        # Get registered tool
        registered_tool = self.registry.get(tool_name)
        if not registered_tool:
            raise ToolError(f"Tool '{tool_name}' not found in registry")
        
        # Parse arguments
        try:
            if isinstance(tool_call.function.get("arguments"), str):
                arguments = json.loads(tool_call.function["arguments"])
            else:
                arguments = tool_call.function.get("arguments", {})
        except json.JSONDecodeError as e:
            raise ToolError(
                f"Failed to parse tool arguments: {str(e)}",
                tool_name=tool_name
            ) from e
        
        # Execute the tool
        result = await self._execute_function(
            registered_tool.function,
            arguments,
            tool_name,
            tool_call.id,
            context
        )
        
        # Record execution
        self._record_execution(
            tool_name=tool_name,
            tool_call_id=tool_call.id,
            arguments=arguments,
            result=result,
            context=context
        )
        
        return result
    
    async def execute_batch(
        self,
        tool_calls: List[ToolCall],
        context: Optional[Dict[str, Any]] = None,
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls
        
        Args:
            tool_calls: List of tool calls to execute
            context: Optional execution context
            parallel: Whether to execute in parallel
            
        Returns:
            List of execution results
        """
        if parallel:
            # Execute in parallel
            tasks = [
                self.execute(tool_call, context)
                for tool_call in tool_calls
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for exceptions and ensure all have proper responses
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    tool_name = tool_calls[i].function.get("name", "unknown")
                    error_msg = str(result)
                    logger.error(f"Tool '{tool_name}' failed: {error_msg}")
                    log_tool_execution(tool_name, "failed", {"error": error_msg})
                    # Create proper error response
                    processed_results.append({
                        "tool_call_id": tool_calls[i].id,
                        "tool_name": tool_name,
                        "content": {
                            "error": ErrorFormatter.get_standard_error_message(
                                tool_name,
                                "failed"
                            )
                        },
                        "success": False
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
        else:
            # Execute sequentially
            results = []
            for tool_call in tool_calls:
                try:
                    result = await self.execute(tool_call, context)
                    results.append(result)
                except Exception as e:
                    tool_name = tool_call.function.get("name", "unknown")
                    error_msg = str(e)
                    logger.error(f"Tool '{tool_name}' failed: {error_msg}")
                    log_tool_execution(tool_name, "failed", {"error": error_msg})
                    # Create proper error response
                    results.append({
                        "tool_call_id": tool_call.id,
                        "tool_name": tool_name,
                        "content": {
                            "error": ErrorFormatter.get_standard_error_message(
                                tool_name,
                                "failed"
                            )
                        },
                        "success": False
                    })
            
            return results
    
    async def _execute_function(
        self,
        func: Callable,
        arguments: Dict[str, Any],
        tool_name: str,
        tool_call_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a tool function
        
        Args:
            func: Function to execute
            arguments: Function arguments
            tool_name: Name of the tool
            tool_call_id: Tool call ID
            context: Execution context
            
        Returns:
            Execution result
        """
        try:
            # Log tool execution start
            log_tool_execution(tool_name, "executing", {"call_id": tool_call_id[:8]})
            
            # Validate arguments
            self._validate_arguments(func, arguments)
            
            # Execute function
            if inspect.iscoroutinefunction(func):
                result = await func(**arguments)
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    func,
                    **arguments
                )
            
            # Format result
            formatted_result = self._format_result(
                result,
                tool_name,
                tool_call_id
            )
            
            # Log success
            log_tool_execution(tool_name, "success")
            
            return formatted_result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tool '{tool_name}' execution failed: {error_msg}")
            log_tool_execution(tool_name, "failed", {"error": error_msg})
            raise ToolError(
                f"Tool execution failed: {error_msg}",
                tool_name=tool_name,
                arguments=arguments
            ) from e
    
    def _validate_arguments(
        self,
        func: Callable,
        arguments: Dict[str, Any]
    ) -> None:
        """
        Validate function arguments
        
        Args:
            func: Function to validate against
            arguments: Arguments to validate
            
        Raises:
            ValidationError: If arguments are invalid
        """
        sig = inspect.signature(func)
        
        # Check for missing required arguments
        required_params = []
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'cls']:
                continue
            if param.default == inspect.Parameter.empty:
                required_params.append(param_name)
        
        missing = set(required_params) - set(arguments.keys())
        if missing:
            raise ValidationError(
                f"Missing required arguments: {missing}"
            )
        
        # Check for unexpected arguments
        valid_params = set(sig.parameters.keys())
        valid_params.discard('self')
        valid_params.discard('cls')
        
        # Check if function accepts **kwargs
        accepts_kwargs = any(
            p.kind == inspect.Parameter.VAR_KEYWORD
            for p in sig.parameters.values()
        )
        
        if not accepts_kwargs:
            extra = set(arguments.keys()) - valid_params
            if extra:
                raise ValidationError(
                    f"Unexpected arguments: {extra}"
                )
    
    def _format_result(
        self,
        result: Any,
        tool_name: str,
        tool_call_id: str
    ) -> Dict[str, Any]:
        """
        Format tool execution result
        
        Args:
            result: Raw execution result
            tool_name: Name of the tool
            tool_call_id: Tool call ID
            
        Returns:
            Formatted result
        """
        # Convert result to serializable format
        if isinstance(result, dict):
            content = result
        else:
            try:
                content = json.loads(json.dumps(result, default=str))
            except Exception:
                content = {"result": str(result)}
        
        return {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "content": content,
            "success": True
        }
    
    def _record_execution(
        self,
        tool_name: str,
        tool_call_id: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> None:
        """
        Record tool execution for history
        
        Args:
            tool_name: Name of executed tool
            tool_call_id: Tool call ID
            arguments: Tool arguments
            result: Execution result
            context: Execution context
        """
        self._execution_count += 1
        
        execution_record = {
            "execution_id": self._execution_count,
            "tool_name": tool_name,
            "tool_call_id": tool_call_id,
            "arguments": arguments,
            "result": result,
            "context": context,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        self._execution_history.append(execution_record)
        
        # Limit history size
        if len(self._execution_history) > 1000:
            self._execution_history = self._execution_history[-500:]
    
    def get_execution_history(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get execution history
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            Execution history records
        """
        if limit:
            return self._execution_history[-limit:]
        return list(self._execution_history)
    
    def clear_history(self) -> None:
        """Clear execution history"""
        self._execution_history.clear()
        self._execution_count = 0
        logger.debug("Cleared tool execution history")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics
        
        Returns:
            Execution statistics
        """
        tool_counts: Dict[str, int] = {}
        total_executions = len(self._execution_history)
        
        for record in self._execution_history:
            tool_name = record["tool_name"]
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
        
        return {
            "total_executions": total_executions,
            "unique_tools": len(tool_counts),
            "tool_counts": tool_counts,
            "registry_size": len(self.registry)
        }