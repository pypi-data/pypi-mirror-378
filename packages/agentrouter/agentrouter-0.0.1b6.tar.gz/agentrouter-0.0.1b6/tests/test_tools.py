"""
Unit tests for tool registration and execution
"""

import pytest
import asyncio
import json
from typing import Dict, Any

from agentrouter.tools import tool, ToolRegistry, ToolExecutor
from agentrouter.types import ToolCall, RegisteredTool
from agentrouter.exceptions import ToolError, ValidationError


class TestToolDecorator:
    """Test the @tool decorator"""
    
    def test_basic_tool_decoration(self):
        """Test basic tool decoration"""
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string"}
                        },
                        "required": ["message"]
                    }
                }
            }
        )
        def test_tool(message: str) -> Dict[str, str]:
            return {"result": f"Received: {message}"}
        
        # Check tool metadata
        assert hasattr(test_tool, '_is_tool')
        assert test_tool._is_tool is True
        assert test_tool._tool_name == "test_tool"
        assert test_tool._tool_definition is not None
        
        # Test execution
        result = test_tool("Hello")
        assert result == {"result": "Received: Hello"}
    
    def test_async_tool_decoration(self):
        """Test async tool decoration"""
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "async_tool",
                    "description": "An async test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "value": {"type": "number"}
                        },
                        "required": ["value"]
                    }
                }
            }
        )
        async def async_tool(value: float) -> Dict[str, float]:
            await asyncio.sleep(0.01)  # Simulate async work
            return {"doubled": value * 2}
        
        # Check it's properly decorated
        assert hasattr(async_tool, '_is_tool')
        assert async_tool._tool_name == "async_tool"
        
        # Test async execution
        async def test():
            result = await async_tool(5.0)
            assert result == {"doubled": 10.0}
        
        asyncio.run(test())
    
    def test_missing_required_params(self):
        """Test validation of missing required parameters"""
        
        with pytest.raises(ValidationError, match="missing required parameters"):
            @tool(
                schema={
                    "type": "function",
                    "function": {
                        "name": "bad_tool",
                        "description": "Tool with mismatch",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "required_param": {"type": "string"}
                            },
                            "required": ["required_param", "missing_param"]
                        }
                    }
                }
            )
            def bad_tool(required_param: str):
                return {"result": required_param}


class TestToolRegistry:
    """Test the ToolRegistry class"""
    
    def test_register_tool(self):
        """Test registering a tool"""
        registry = ToolRegistry("test")
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "sample_tool",
                    "description": "Sample tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data": {"type": "string"}
                        },
                        "required": ["data"]
                    }
                }
            }
        )
        def sample_tool(data: str):
            return {"processed": data}
        
        # Register the tool
        registry.register(sample_tool)
        
        # Check registration
        assert registry.has("sample_tool")
        assert len(registry) == 1
        assert "sample_tool" in registry.list_tools()
        
        # Get the tool
        registered = registry.get("sample_tool")
        assert registered is not None
        assert registered.name == "sample_tool"
    
    def test_register_with_alias(self):
        """Test registering a tool with an alias"""
        registry = ToolRegistry("test")
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "original_name",
                    "description": "Tool with alias",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        )
        def my_tool():
            return {"status": "ok"}
        
        # Register with alias
        registry.register(my_tool, alias="shortcut")
        
        # Check both names work
        assert registry.has("original_name")
        assert registry.get("shortcut") is not None
        assert registry.get("shortcut").name == "original_name"
    
    def test_unregister_tool(self):
        """Test unregistering a tool"""
        registry = ToolRegistry("test")
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "temp_tool",
                    "description": "Temporary tool",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        )
        def temp_tool():
            return {}
        
        registry.register(temp_tool)
        assert registry.has("temp_tool")
        
        # Unregister
        result = registry.unregister("temp_tool")
        assert result is True
        assert not registry.has("temp_tool")
        assert len(registry) == 0
    
    def test_registry_locking(self):
        """Test registry locking mechanism"""
        registry = ToolRegistry("test")
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "tool1",
                    "description": "Tool 1",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        )
        def tool1():
            return {}
        
        registry.register(tool1)
        
        # Lock the registry
        registry.lock()
        assert registry.is_locked()
        
        # Try to register while locked
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "tool2",
                    "description": "Tool 2",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
        )
        def tool2():
            return {}
        
        with pytest.raises(ToolError, match="locked registry"):
            registry.register(tool2)
        
        # Unlock and register
        registry.unlock()
        assert not registry.is_locked()
        registry.register(tool2)
        assert registry.has("tool2")


class TestToolExecutor:
    """Test the ToolExecutor class"""
    
    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test executing a tool"""
        registry = ToolRegistry("test")
        executor = ToolExecutor(registry)
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "compute",
                    "description": "Compute something",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"}
                        },
                        "required": ["x", "y"]
                    }
                }
            }
        )
        def compute(x: float, y: float) -> Dict[str, float]:
            return {"sum": x + y, "product": x * y}
        
        registry.register(compute)
        
        # Create a tool call
        tool_call = ToolCall(
            id="call_001",
            type="function",
            function={
                "name": "compute",
                "arguments": json.dumps({"x": 3, "y": 4})
            }
        )
        
        # Execute
        result = await executor.execute(tool_call)
        
        # Check result
        assert result["tool_call_id"] == "call_001"
        assert result["tool_name"] == "compute"
        assert result["success"] is True
        assert result["content"]["sum"] == 7
        assert result["content"]["product"] == 12
    
    @pytest.mark.asyncio
    async def test_execute_missing_tool(self):
        """Test executing a non-existent tool"""
        registry = ToolRegistry("test")
        executor = ToolExecutor(registry)
        
        tool_call = ToolCall(
            id="call_002",
            type="function",
            function={
                "name": "non_existent",
                "arguments": "{}"
            }
        )
        
        with pytest.raises(ToolError, match="not found"):
            await executor.execute(tool_call)
    
    @pytest.mark.asyncio
    async def test_execute_batch(self):
        """Test executing multiple tools in batch"""
        registry = ToolRegistry("test")
        executor = ToolExecutor(registry)
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "add",
                    "description": "Add two numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["a", "b"]
                    }
                }
            }
        )
        def add(a: float, b: float) -> float:
            return a + b
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "multiply",
                    "description": "Multiply two numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["a", "b"]
                    }
                }
            }
        )
        def multiply(a: float, b: float) -> float:
            return a * b
        
        registry.register(add)
        registry.register(multiply)
        
        # Create multiple tool calls
        tool_calls = [
            ToolCall(
                id="call_003",
                type="function",
                function={
                    "name": "add",
                    "arguments": json.dumps({"a": 5, "b": 3})
                }
            ),
            ToolCall(
                id="call_004",
                type="function",
                function={
                    "name": "multiply",
                    "arguments": json.dumps({"a": 4, "b": 7})
                }
            )
        ]
        
        # Execute batch
        results = await executor.execute_batch(tool_calls, parallel=True)
        
        # Check results
        assert len(results) == 2
        assert results[0]["tool_call_id"] == "call_003"
        assert results[0]["content"] == 8
        assert results[1]["tool_call_id"] == "call_004"
        assert results[1]["content"] == 28
    
    @pytest.mark.asyncio
    async def test_invalid_arguments(self):
        """Test executing a tool with invalid arguments"""
        registry = ToolRegistry("test")
        executor = ToolExecutor(registry)
        
        @tool(
            schema={
                "type": "function",
                "function": {
                    "name": "strict_tool",
                    "description": "Tool with strict params",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "required_param": {"type": "string"}
                        },
                        "required": ["required_param"]
                    }
                }
            }
        )
        def strict_tool(required_param: str) -> str:
            return required_param.upper()
        
        registry.register(strict_tool)
        
        # Call without required parameter
        tool_call = ToolCall(
            id="call_005",
            type="function",
            function={
                "name": "strict_tool",
                "arguments": json.dumps({})  # Missing required_param
            }
        )
        
        with pytest.raises(ToolError, match="Missing required arguments"):
            await executor.execute(tool_call)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])