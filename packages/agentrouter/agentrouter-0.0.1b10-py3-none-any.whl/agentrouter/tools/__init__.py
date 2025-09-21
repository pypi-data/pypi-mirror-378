"""
Tool registration and management for AgentRouter SDK
"""

from agentrouter.tools.decorator import tool
from agentrouter.tools.registry import ToolRegistry
from agentrouter.tools.executor import ToolExecutor

__all__ = [
    "tool",
    "ToolRegistry",
    "ToolExecutor",
]