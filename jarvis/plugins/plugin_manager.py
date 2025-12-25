#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/JARVIS - Plugin Manager
Manages loading, unloading, and execution of plugins.
"""

import importlib
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
import logging

from .plugin_interface import PluginInterface, PluginStatus, PluginPriority
from utils.exceptions import PluginLoadError, PluginNotFoundError, PluginExecutionError

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Manager for ALEX/JARVIS plugins.
    Handles plugin lifecycle: discovery, loading, activation, execution, and unloading.
    """
    
    def __init__(self, plugin_dirs: List[Path] = None):
        """
        Initialize plugin manager.
        
        Args:
            plugin_dirs: List of directories to search for plugins
        """
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_dirs = plugin_dirs or [Path(__file__).parent / "builtin"]
        self.execution_order: List[str] = []
        
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in plugin directories.
        
        Returns:
            List[str]: List of discovered plugin names
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
                
            for file_path in plugin_dir.glob("*_plugin.py"):
                plugin_name = file_path.stem
                discovered.append(plugin_name)
                logger.info(f"Discovered plugin: {plugin_name}")
                
        return discovered
        
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Load a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            bool: True if loaded successfully
            
        Raises:
            PluginLoadError: If plugin fails to load
        """
        try:
            # Find plugin file
            plugin_path = None
            for plugin_dir in self.plugin_dirs:
                candidate = plugin_dir / f"{plugin_name}.py"
                if candidate.exists():
                    plugin_path = candidate
                    break
                    
            if not plugin_path:
                raise PluginNotFoundError(f"Plugin not found: {plugin_name}")
                
            # Import module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    plugin_class = obj
                    break
                    
            if not plugin_class:
                raise PluginLoadError(f"No plugin class found in {plugin_name}")
                
            # Instantiate plugin
            plugin = plugin_class()
            
            # Call on_load
            if not plugin.on_load():
                raise PluginLoadError(f"Plugin on_load failed: {plugin_name}")
                
            # Store plugin
            self.plugins[plugin_name] = plugin
            plugin.metadata = plugin.get_metadata()
            
            # Update execution order
            self._update_execution_order()
            
            logger.info(f"✅ Plugin loaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
            raise PluginLoadError(f"Failed to load plugin: {plugin_name}") from e
            
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            bool: True if unloaded successfully
        """
        if plugin_name not in self.plugins:
            raise PluginNotFoundError(f"Plugin not loaded: {plugin_name}")
            
        try:
            plugin = self.plugins[plugin_name]
            plugin.on_unload()
            plugin.set_status(PluginStatus.UNLOADED)
            del self.plugins[plugin_name]
            
            # Update execution order
            self._update_execution_order()
            
            logger.info(f"Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
            
    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a plugin."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].activate()
        return False
        
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate a plugin."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].deactivate()
        return False
        
    def execute_command(self, command: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Execute a command through plugins.
        
        Args:
            command: User command
            context: Context dictionary
            
        Returns:
            Optional[str]: Plugin response or None
        """
        for plugin_name in self.execution_order:
            plugin = self.plugins[plugin_name]
            
            if not plugin.is_active():
                continue
                
            try:
                if plugin.can_handle(command, context):
                    response = plugin.handle_command(command, context)
                    if response:
                        logger.info(f"Command handled by plugin: {plugin_name}")
                        return response
            except Exception as e:
                logger.error(f"Error executing plugin {plugin_name}: {e}")
                raise PluginExecutionError(f"Plugin execution failed: {plugin_name}") from e
                
        return None
        
    def trigger_before_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """Trigger before_response hooks."""
        modified_input = user_input
        
        for plugin_name in self.execution_order:
            plugin = self.plugins[plugin_name]
            if plugin.is_active():
                result = plugin.on_before_response(modified_input, context)
                if result:
                    modified_input = result
                    
        return modified_input
        
    def trigger_after_response(self, response: str, context: Dict[str, Any]) -> str:
        """Trigger after_response hooks."""
        modified_response = response
        
        for plugin_name in self.execution_order:
            plugin = self.plugins[plugin_name]
            if plugin.is_active():
                result = plugin.on_after_response(modified_response, context)
                if result:
                    modified_response = result
                    
        return modified_response
        
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get a plugin by name."""
        return self.plugins.get(plugin_name)
        
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins."""
        result = []
        for name, plugin in self.plugins.items():
            metadata = plugin.get_metadata()
            result.append({
                "name": name,
                "version": metadata.version,
                "status": plugin.get_status().value,
                "active": plugin.is_active(),
                "capabilities": plugin.get_capabilities(),
                "priority": metadata.priority.value
            })
        return result
        
    def _update_execution_order(self):
        """Update plugin execution order based on priority."""
        sorted_plugins = sorted(
            self.plugins.items(),
            key=lambda x: x[1].get_metadata().priority.value,
            reverse=True
        )
        self.execution_order = [name for name, _ in sorted_plugins]
        
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        if plugin_name in self.plugins:
            self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name)
        
    def load_all(self) -> int:
        """Load all discovered plugins."""
        discovered = self.discover_plugins()
        loaded_count = 0
        
        for plugin_name in discovered:
            try:
                if self.load_plugin(plugin_name):
                    loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load {plugin_name}: {e}")
                
        return loaded_count
