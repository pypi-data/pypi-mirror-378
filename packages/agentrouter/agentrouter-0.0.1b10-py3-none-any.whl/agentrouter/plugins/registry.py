"""
Plugin registry for managing plugins in AgentRouter SDK
"""

import logging
from typing import Any, Dict, List, Optional, Set

from agentrouter.exceptions import PluginError, ValidationError
from agentrouter.plugins.base import Plugin, PluginHook


logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Registry for managing plugins
    """
    
    def __init__(self, name: str = "default"):
        """
        Initialize plugin registry
        
        Args:
            name: Registry name for identification
        """
        self.name = name
        self._plugins: Dict[str, Plugin] = {}
        self._hook_map: Dict[PluginHook, List[Plugin]] = {}
        self._execution_order: List[str] = []
        self._locked = False
        
        logger.debug(f"Created plugin registry: {name}")
    
    def register(
        self,
        plugin: Plugin,
        priority: Optional[int] = None
    ) -> None:
        """
        Register a plugin
        
        Args:
            plugin: Plugin instance to register
            priority: Optional priority (lower executes first)
            
        Raises:
            PluginError: If plugin already registered or registry is locked
            ValidationError: If plugin is invalid
        """
        if self._locked:
            raise PluginError(
                f"Cannot register plugins in locked registry: {self.name}"
            )
        
        if not isinstance(plugin, Plugin):
            raise ValidationError(
                f"Invalid plugin type: {type(plugin)}"
            )
        
        plugin_name = plugin.name
        
        if plugin_name in self._plugins:
            raise PluginError(
                f"Plugin '{plugin_name}' already registered"
            )
        
        # Register plugin
        self._plugins[plugin_name] = plugin
        
        # Add to execution order
        if priority is not None:
            # Insert at appropriate position based on priority
            self._execution_order.insert(priority, plugin_name)
        else:
            self._execution_order.append(plugin_name)
        
        # Map hooks
        for hook in plugin.get_hooks():
            if hook not in self._hook_map:
                self._hook_map[hook] = []
            self._hook_map[hook].append(plugin)
        
        # Initialize plugin
        try:
            plugin.initialize({"registry": self.name})
        except Exception as e:
            logger.warning(
                f"Plugin '{plugin_name}' initialization failed: {str(e)}"
            )
        
        logger.info(
            f"Registered plugin '{plugin_name}' in registry '{self.name}'"
        )
    
    def unregister(self, name: str) -> bool:
        """
        Unregister a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was unregistered
        """
        if self._locked:
            raise PluginError(
                f"Cannot unregister plugins from locked registry: {self.name}"
            )
        
        if name not in self._plugins:
            return False
        
        plugin = self._plugins[name]
        
        # Cleanup plugin
        try:
            plugin.cleanup()
        except Exception as e:
            logger.warning(
                f"Plugin '{name}' cleanup failed: {str(e)}"
            )
        
        # Remove from hook map
        for hook, plugins in self._hook_map.items():
            if plugin in plugins:
                plugins.remove(plugin)
        
        # Remove from registry
        del self._plugins[name]
        self._execution_order.remove(name)
        
        logger.info(f"Unregistered plugin '{name}' from registry '{self.name}'")
        return True
    
    def get(self, name: str) -> Optional[Plugin]:
        """
        Get a registered plugin by name
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin if found, None otherwise
        """
        return self._plugins.get(name)
    
    def has(self, name: str) -> bool:
        """
        Check if a plugin is registered
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin is registered
        """
        return name in self._plugins
    
    def list_plugins(self) -> List[str]:
        """
        List all registered plugin names
        
        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())
    
    def get_all_plugins(self) -> List[Plugin]:
        """
        Get all registered plugins in execution order
        
        Returns:
            List of all plugins
        """
        return [
            self._plugins[name]
            for name in self._execution_order
            if name in self._plugins
        ]
    
    def get_plugins_for_hook(
        self,
        hook: PluginHook
    ) -> List[Plugin]:
        """
        Get plugins that handle a specific hook
        
        Args:
            hook: Plugin hook
            
        Returns:
            List of plugins for the hook
        """
        plugins = self._hook_map.get(hook, [])
        
        # Return only enabled plugins in execution order
        ordered_plugins = []
        for name in self._execution_order:
            if name in self._plugins:
                plugin = self._plugins[name]
                if plugin in plugins and plugin.is_enabled():
                    ordered_plugins.append(plugin)
        
        return ordered_plugins
    
    async def execute_hook(
        self,
        hook: PluginHook,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute all plugins for a specific hook
        
        Args:
            hook: Plugin hook to execute
            context: Context to pass to plugins
            
        Returns:
            Modified context after all plugins
        """
        plugins = self.get_plugins_for_hook(hook)
        
        for plugin in plugins:
            try:
                # Get the hook method
                hook_method = getattr(plugin, hook.value, None)
                
                if hook_method and callable(hook_method):
                    # Execute hook
                    context = hook_method(context)
                    
                    # Log execution
                    logger.debug(
                        f"Executed hook '{hook.value}' for plugin '{plugin.name}'"
                    )
                    
            except Exception as e:
                logger.error(
                    f"Plugin '{plugin.name}' hook '{hook.value}' failed: {str(e)}",
                    exc_info=True
                )
                # Continue with other plugins
        
        return context
    
    def enable_plugin(self, name: str) -> bool:
        """
        Enable a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was enabled
        """
        plugin = self.get(name)
        if plugin:
            plugin.enable()
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """
        Disable a plugin
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was disabled
        """
        plugin = self.get(name)
        if plugin:
            plugin.disable()
            return True
        return False
    
    def clear(self) -> None:
        """
        Clear all registered plugins
        """
        if self._locked:
            raise PluginError(
                f"Cannot clear locked registry: {self.name}"
            )
        
        # Cleanup all plugins
        for plugin in self._plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.warning(
                    f"Plugin '{plugin.name}' cleanup failed: {str(e)}"
                )
        
        self._plugins.clear()
        self._hook_map.clear()
        self._execution_order.clear()
        
        logger.info(f"Cleared all plugins from registry '{self.name}'")
    
    def lock(self) -> None:
        """
        Lock the registry to prevent modifications
        """
        self._locked = True
        logger.info(f"Locked plugin registry '{self.name}'")
    
    def unlock(self) -> None:
        """
        Unlock the registry to allow modifications
        """
        self._locked = False
        logger.info(f"Unlocked plugin registry '{self.name}'")
    
    def is_locked(self) -> bool:
        """
        Check if registry is locked
        
        Returns:
            True if registry is locked
        """
        return self._locked
    
    def get_plugin_info(self) -> List[Dict[str, Any]]:
        """
        Get information about all registered plugins
        
        Returns:
            List of plugin information dictionaries
        """
        info = []
        
        for name in self._execution_order:
            if name in self._plugins:
                plugin = self._plugins[name]
                info.append({
                    "name": plugin.name,
                    "version": plugin.version,
                    "enabled": plugin.is_enabled(),
                    "hooks": [hook.value for hook in plugin.get_hooks()],
                    "metadata": plugin._metadata
                })
        
        return info
    
    def set_execution_order(self, order: List[str]) -> None:
        """
        Set custom execution order for plugins
        
        Args:
            order: List of plugin names in desired order
            
        Raises:
            ValidationError: If order contains unknown plugins
        """
        if self._locked:
            raise PluginError(
                f"Cannot modify locked registry: {self.name}"
            )
        
        # Validate all plugins exist
        unknown = set(order) - set(self._plugins.keys())
        if unknown:
            raise ValidationError(
                f"Unknown plugins in order: {unknown}"
            )
        
        # Ensure all plugins are included
        missing = set(self._plugins.keys()) - set(order)
        if missing:
            # Add missing plugins at the end
            order.extend(missing)
        
        self._execution_order = order
        
        logger.info(f"Set custom execution order for registry '{self.name}'")
    
    def __len__(self) -> int:
        """Get number of registered plugins"""
        return len(self._plugins)
    
    def __contains__(self, name: str) -> bool:
        """Check if plugin is registered"""
        return name in self._plugins
    
    def __repr__(self) -> str:
        """String representation"""
        return (
            f"PluginRegistry(name='{self.name}', "
            f"plugins={len(self._plugins)}, "
            f"locked={self._locked})"
        )