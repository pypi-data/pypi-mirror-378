"""
Tool decorator for AgentRouter SDK
"""

import asyncio
import functools
import inspect
import json
import logging
from typing import Any, Callable, Dict, Optional

from agentrouter.api import get_utility_client
from agentrouter.exceptions import ValidationError
from agentrouter.types import ToolDefinition, FunctionDefinition, RegisteredTool


logger = logging.getLogger(__name__)


def tool(
    schema: Dict[str, Any],
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Callable:
    """
    Decorator to register a function as a tool
    
    Args:
        schema: OpenAI-compatible tool schema
        name: Optional tool name (defaults to function name)
        description: Optional tool description
        
    Returns:
        Decorated function
        
    Example:
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "search_kb",
                    "description": "Search knowledge base",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }
        )
        def search_kb(query: str):
            return {"results": f"Found: {query}"}
    """
    def decorator(func: Callable) -> Callable:
        # Import validator here to avoid circular imports
        from agentrouter.validators.format_validators import FormatValidator
        
        # CRITICAL: Validate that function is async FIRST (fail-fast)
        try:
            FormatValidator.validate_async_function(func, func.__name__)
        except ValueError as e:
            # Re-raise with ValidationError for consistency
            raise ValidationError(str(e))
        
        # Validate schema
        if not schema:
            raise ValidationError("Tool schema is required")
        
        # Use comprehensive schema validation
        try:
            validated_schema = FormatValidator.validate_tool_schema(schema)
        except ValueError as e:
            raise ValidationError(str(e))
        
        function_def = validated_schema["function"]
        
        # Validate tool schema using validate-tools API (additional validation)
        _validate_tool_schema_with_api(validated_schema)
        
        # Extract tool information
        tool_name = name or function_def["name"] or func.__name__
        tool_description = (
            description or 
            function_def.get("description") or 
            func.__doc__ or 
            "No description available"
        )
        
        # Validate function signature matches schema
        _validate_function_signature(func, function_def["parameters"])
        
        # Create tool definition
        function_definition = FunctionDefinition(
            name=tool_name,
            description=tool_description,
            parameters=function_def["parameters"]
        )
        
        tool_definition = ToolDefinition(
            type="function",
            function=function_definition
        )
        
        # Create async wrapper (all tools MUST be async now)
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            """Async wrapper for tool function"""
            try:
                # Log tool execution
                logger.debug(f"Executing tool: {tool_name}")
                
                # Execute async function (we've already validated it's async)
                result = await func(*args, **kwargs)
                
                logger.debug(f"Tool {tool_name} completed successfully")
                return result
                
            except Exception as e:
                logger.error(
                    f"Tool {tool_name} failed: {str(e)}",
                    exc_info=True
                )
                raise
        
        # Always use async wrapper (no sync wrapper needed anymore)
        wrapper = async_wrapper
        
        # Attach metadata to wrapper
        wrapper._tool_definition = tool_definition
        wrapper._tool_name = tool_name
        wrapper._tool_schema = schema
        wrapper._is_tool = True
        wrapper._original_func = func
        
        return wrapper
    
    return decorator


def _validate_tool_schema_with_api(schema: Dict[str, Any]) -> None:
    """
    Validate tool schema using the validate-tools API
    
    Args:
        schema: Tool schema to validate
        
    Raises:
        ValidationError: If schema is invalid
    """
    try:
        # Get utility client
        utility_client = get_utility_client()
        
        # Create event loop if not exists (for sync context)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Validate the tool schema
        result = loop.run_until_complete(
            utility_client.validate_tools([schema])
        )
        
        # Check validation result
        if result and result.get("status") == 1:
            logger.debug(f"Tool schema validated successfully: {schema['function']['name']}")
        else:
            error_message = result.get("message", "Unknown validation error") if result else "Validation failed"
            raise ValidationError(
                f"Tool schema validation failed: {error_message}",
                field="schema",
                value=schema,
                details=result.get("data", {}) if result else {}
            )
            
    except ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Log warning but don't fail - allow tool registration to continue
        logger.warning(
            f"Could not validate tool schema with API (will proceed with local validation): {str(e)}"
        )


def _validate_function_signature(
    func: Callable,
    parameters_schema: Dict[str, Any]
) -> None:
    """
    Validate that function signature matches schema parameters
    
    Args:
        func: Function to validate
        parameters_schema: Parameters schema from tool definition
        
    Raises:
        ValidationError: If signature doesn't match schema
    """
    # Get function signature
    sig = inspect.signature(func)
    func_params = set(sig.parameters.keys())
    
    # Get schema parameters
    schema_properties = parameters_schema.get("properties", {})
    schema_params = set(schema_properties.keys())
    required_params = set(parameters_schema.get("required", []))
    
    # Remove 'self' and 'cls' from function parameters if present
    func_params.discard('self')
    func_params.discard('cls')
    
    # Check required parameters
    missing_required = required_params - func_params
    if missing_required:
        raise ValidationError(
            f"Function {func.__name__} missing required parameters: {missing_required}"
        )
    
    # Check for extra parameters not in schema
    extra_params = func_params - schema_params
    if extra_params and not parameters_schema.get("additionalProperties", False):
        # Allow extra params if they have defaults
        for param in extra_params:
            if sig.parameters[param].default == inspect.Parameter.empty:
                raise ValidationError(
                    f"Function {func.__name__} has parameters not in schema: {extra_params}"
                )
    
    # Validate parameter types if specified
    for param_name, param_info in sig.parameters.items():
        if param_name in ['self', 'cls']:
            continue
            
        if param_name in schema_properties:
            schema_type = schema_properties[param_name].get("type")
            
            # Basic type validation (can be extended)
            if param_info.annotation != inspect.Parameter.empty:
                python_type = param_info.annotation
                
                # Map schema types to Python types
                type_mapping = {
                    "string": str,
                    "number": (int, float),
                    "integer": int,
                    "boolean": bool,
                    "array": list,
                    "object": dict,
                }
                
                if schema_type in type_mapping:
                    expected_type = type_mapping[schema_type]
                    
                    # Check if annotation matches expected type
                    if not _is_compatible_type(python_type, expected_type):
                        logger.warning(
                            f"Parameter {param_name} type mismatch: "
                            f"schema expects {schema_type}, "
                            f"function has {python_type}"
                        )


def _is_compatible_type(annotation: Any, expected_type: Any) -> bool:
    """
    Check if annotation is compatible with expected type
    
    Args:
        annotation: Type annotation from function
        expected_type: Expected type from schema
        
    Returns:
        True if types are compatible
    """
    # Handle Union types
    if hasattr(annotation, '__origin__'):
        if annotation.__origin__ == type(Optional):
            # For Optional types, check the inner type
            inner_types = annotation.__args__
            return any(_is_compatible_type(t, expected_type) for t in inner_types if t != type(None))
    
    # Handle tuple of types
    if isinstance(expected_type, tuple):
        return any(annotation == t or annotation is t for t in expected_type)
    
    # Direct comparison
    return annotation == expected_type or annotation is expected_type


def is_tool(func: Callable) -> bool:
    """
    Check if a function is decorated as a tool
    
    Args:
        func: Function to check
        
    Returns:
        True if function is a tool
    """
    return hasattr(func, '_is_tool') and func._is_tool


def get_tool_definition(func: Callable) -> Optional[ToolDefinition]:
    """
    Get tool definition from a decorated function
    
    Args:
        func: Decorated function
        
    Returns:
        Tool definition if function is a tool, None otherwise
    """
    if is_tool(func):
        return func._tool_definition
    return None


def get_tool_name(func: Callable) -> Optional[str]:
    """
    Get tool name from a decorated function
    
    Args:
        func: Decorated function
        
    Returns:
        Tool name if function is a tool, None otherwise
    """
    if is_tool(func):
        return func._tool_name
    return None