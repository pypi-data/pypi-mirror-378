"""
Plugin system for AgentRouter SDK
"""

from agentrouter.plugins.base import Plugin, PluginHook
from agentrouter.plugins.registry import PluginRegistry

__all__ = [
    "Plugin",
    "PluginHook",
    "PluginRegistry",
]