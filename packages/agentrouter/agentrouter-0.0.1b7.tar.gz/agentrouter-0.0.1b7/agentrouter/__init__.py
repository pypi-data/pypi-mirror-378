"""
AgentRouter SDK - A Python SDK for building scalable multi-agent applications
"""

from agentrouter.agents.manager import ManagerAgent
from agentrouter.agents.worker import WorkerAgent
from agentrouter.tools.decorator import tool
from agentrouter.plugins.base import Plugin, PluginHook
from agentrouter.exceptions import (
    AgentRouterError,
    APIError,
    ValidationError,
    ExecutionError,
    ToolError,
)
from agentrouter.utils.logging import LoggingManager, get_logger

__version__ = "0.0.1b7"
__author__ = "AgentRouter Team"
__email__ = "support@us.inc"

__all__ = [
    # Agents
    "ManagerAgent",
    "WorkerAgent",
    
    # Tools
    "tool",
    
    # Plugins
    "Plugin",
    "PluginHook",
    
    # Exceptions
    "AgentRouterError",
    "APIError",
    "ValidationError",
    "ExecutionError",
    "ToolError",
    
    # Logging
    "get_logger",
]

# Initialize logging system
# The LoggingManager singleton will be created and configured automatically
# when the module is imported
_log_manager = LoggingManager()