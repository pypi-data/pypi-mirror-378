"""
Tool registry for managing registered tools
"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Set

from agentrouter.exceptions import ToolError, ValidationError
from agentrouter.types import RegisteredTool, ToolDefinition
from agentrouter.tools.decorator import is_tool, get_tool_definition, get_tool_name


logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registry for managing tools
    """
    
    def __init__(self, name: str = "default"):
        """
        Initialize tool registry
        
        Args:
            name: Registry name for identification
        """
        self.name = name
        self._tools: Dict[str, RegisteredTool] = {}
        self._tool_aliases: Dict[str, str] = {}
        self._locked = False
        
        logger.debug(f"Created tool registry: {name}")
    
    def register(
        self,
        func: Callable,
        alias: Optional[str] = None,
        override: bool = False
    ) -> None:
        """
        Register a tool function
        
        Args:
            func: Tool function (must be decorated with @tool)
            alias: Optional alias for the tool
            override: Whether to override existing tool
            
        Raises:
            ValidationError: If function is not a valid tool
            ToolError: If tool already exists and override is False
        """
        # Check if registry is locked
        if self._locked:
            raise ToolError(
                f"Cannot register tools in locked registry: {self.name}"
            )
        
        # Validate function is a tool
        if not is_tool(func):
            raise ValidationError(
                f"Function {func.__name__} is not decorated with @tool"
            )
        
        # Get tool information
        tool_name = get_tool_name(func)
        tool_definition = get_tool_definition(func)
        
        if not tool_name or not tool_definition:
            raise ValidationError(
                f"Could not extract tool information from {func.__name__}"
            )
        
        # Check for existing tool
        if tool_name in self._tools and not override:
            raise ToolError(
                f"Tool '{tool_name}' already registered. Set override=True to replace."
            )
        
        # Create registered tool
        registered_tool = RegisteredTool(
            name=tool_name,
            function=func,
            schema=tool_definition,
            description=tool_definition.function.description
        )
        
        # Register the tool
        self._tools[tool_name] = registered_tool
        
        # Register alias if provided
        if alias:
            self._tool_aliases[alias] = tool_name
        
        logger.info(
            f"Registered tool '{tool_name}' in registry '{self.name}'"
            + (f" with alias '{alias}'" if alias else "")
        )
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a tool
        
        Args:
            name: Tool name or alias
            
        Returns:
            True if tool was unregistered, False if not found
        """
        # Check if registry is locked
        if self._locked:
            raise ToolError(
                f"Cannot unregister tools from locked registry: {self.name}"
            )
        
        # Resolve alias
        tool_name = self._resolve_name(name)
        
        if tool_name in self._tools:
            del self._tools[tool_name]
            
            # Remove any aliases
            aliases_to_remove = [
                alias for alias, target in self._tool_aliases.items()
                if target == tool_name
            ]
            for alias in aliases_to_remove:
                del self._tool_aliases[alias]
            
            logger.info(f"Unregistered tool '{tool_name}' from registry '{self.name}'")
            return True
        
        return False
    
    def get(self, name: str) -> Optional[RegisteredTool]:
        """
        Get a registered tool by name
        
        Args:
            name: Tool name or alias
            
        Returns:
            Registered tool if found, None otherwise
        """
        tool_name = self._resolve_name(name)
        return self._tools.get(tool_name)
    
    def has(self, name: str) -> bool:
        """
        Check if a tool is registered
        
        Args:
            name: Tool name or alias
            
        Returns:
            True if tool is registered
        """
        return self.get(name) is not None
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def list_aliases(self) -> Dict[str, str]:
        """
        List all tool aliases
        
        Returns:
            Dictionary mapping aliases to tool names
        """
        return dict(self._tool_aliases)
    
    def get_all_tools(self) -> List[RegisteredTool]:
        """
        Get all registered tools
        
        Returns:
            List of all registered tools
        """
        return list(self._tools.values())
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """
        Get all tool definitions for API calls
        
        Returns:
            List of tool definitions
        """
        return [tool.schema for tool in self._tools.values()]
    
    def clear(self) -> None:
        """
        Clear all registered tools
        """
        if self._locked:
            raise ToolError(
                f"Cannot clear locked registry: {self.name}"
            )
        
        self._tools.clear()
        self._tool_aliases.clear()
        logger.info(f"Cleared all tools from registry '{self.name}'")
    
    def lock(self) -> None:
        """
        Lock the registry to prevent modifications
        """
        self._locked = True
        logger.info(f"Locked registry '{self.name}'")
    
    def unlock(self) -> None:
        """
        Unlock the registry to allow modifications
        """
        self._locked = False
        logger.info(f"Unlocked registry '{self.name}'")
    
    def is_locked(self) -> bool:
        """
        Check if registry is locked
        
        Returns:
            True if registry is locked
        """
        return self._locked
    
    def merge(self, other: 'ToolRegistry', override: bool = False) -> None:
        """
        Merge another registry into this one
        
        Args:
            other: Registry to merge from
            override: Whether to override existing tools
        """
        if self._locked:
            raise ToolError(
                f"Cannot merge into locked registry: {self.name}"
            )
        
        for tool in other.get_all_tools():
            try:
                # Re-register the tool's function
                self.register(tool.function, override=override)
            except ToolError as e:
                if not override:
                    logger.warning(
                        f"Skipping tool '{tool.name}' during merge: {str(e)}"
                    )
        
        # Merge aliases
        for alias, tool_name in other.list_aliases().items():
            if alias not in self._tool_aliases:
                self._tool_aliases[alias] = tool_name
        
        logger.info(
            f"Merged {len(other._tools)} tools from registry '{other.name}' "
            f"into registry '{self.name}'"
        )
    
    def clone(self, name: Optional[str] = None) -> 'ToolRegistry':
        """
        Create a clone of this registry
        
        Args:
            name: Name for the cloned registry
            
        Returns:
            Cloned registry
        """
        cloned = ToolRegistry(name or f"{self.name}_clone")
        cloned.merge(self, override=True)
        return cloned
    
    def _resolve_name(self, name: str) -> str:
        """
        Resolve a name to actual tool name (handling aliases)
        
        Args:
            name: Tool name or alias
            
        Returns:
            Actual tool name
        """
        return self._tool_aliases.get(name, name)
    
    def validate_schema_match(self, func: Callable, tool_name: str) -> bool:
        """
        Validate that a function matches the registered tool's schema
        
        Args:
            func: Function to validate
            tool_name: Name of registered tool
            
        Returns:
            True if function matches schema
            
        Raises:
            ValidationError: If validation fails
        """
        registered_tool = self.get(tool_name)
        if not registered_tool:
            raise ValidationError(f"Tool '{tool_name}' not found in registry")
        
        # Get function signature
        sig = inspect.signature(func)
        func_params = set(sig.parameters.keys())
        func_params.discard('self')
        func_params.discard('cls')
        
        # Get schema parameters
        schema = registered_tool.schema.function.parameters
        required_params = set(schema.get("required", []))
        
        # Check required parameters
        missing = required_params - func_params
        if missing:
            raise ValidationError(
                f"Function missing required parameters for tool '{tool_name}': {missing}"
            )
        
        return True
    
    def __len__(self) -> int:
        """Get number of registered tools"""
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        """Check if tool is registered"""
        return self.has(name)
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"ToolRegistry(name='{self.name}', "
            f"tools={len(self._tools)}, "
            f"locked={self._locked})"
        )