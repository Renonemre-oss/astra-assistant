#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ALEX/Astra - Plugin Interface
Base interface for all plugins in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin status."""
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UNLOADED = "unloaded"


class PluginPriority(Enum):
    """Plugin execution priority."""
    CRITICAL = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    BACKGROUND = 10


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    author: str
    description: str
    dependencies: List[str]
    capabilities: List[str]
    priority: PluginPriority = PluginPriority.NORMAL
    enabled: bool = True


class PluginInterface(ABC):
    """
    Base interface for all ALEX/Astra plugins.
    
    All plugins must inherit from this class and implement the required methods.
    """
    
    def __init__(self):
        self.status = PluginStatus.LOADED
        self.metadata: Optional[PluginMetadata] = None
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.
        
        Returns:
            PluginMetadata: Plugin information
        """
        pass
        
    @abstractmethod
    def on_load(self) -> bool:
        """
        Called when plugin is loaded.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        pass
        
    @abstractmethod
    def on_unload(self) -> bool:
        """
        Called when plugin is unloaded.
        
        Returns:
            bool: True if unloaded successfully, False otherwise
        """
        pass
        
    @abstractmethod
    def handle_command(self, command: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Handle a command from the user.
        
        Args:
            command: User command
            context: Context dictionary with user info, conversation history, etc.
            
        Returns:
            Optional[str]: Response string or None if command not handled
        """
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of plugin capabilities.
        
        Returns:
            List[str]: List of capability names
        """
        pass
        
    def can_handle(self, command: str, context: Dict[str, Any]) -> bool:
        """
        Check if plugin can handle a command.
        
        Args:
            command: User command
            context: Context dictionary
            
        Returns:
            bool: True if plugin can handle this command
        """
        return False
        
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the plugin.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            bool: True if configured successfully
        """
        self.config = config
        return True
        
    def get_config(self) -> Dict[str, Any]:
        """
        Get plugin configuration.
        
        Returns:
            Dict[str, Any]: Current configuration
        """
        return self.config
        
    def set_status(self, status: PluginStatus):
        """Set plugin status."""
        self.status = status
        self.logger.info(f"Plugin status changed to: {status.value}")
        
    def get_status(self) -> PluginStatus:
        """Get plugin status."""
        return self.status
        
    def is_active(self) -> bool:
        """Check if plugin is active."""
        return self.status == PluginStatus.ACTIVE
        
    def activate(self) -> bool:
        """
        Activate the plugin.
        
        Returns:
            bool: True if activated successfully
        """
        if self.status == PluginStatus.LOADED or self.status == PluginStatus.INACTIVE:
            self.set_status(PluginStatus.ACTIVE)
            return True
        return False
        
    def deactivate(self) -> bool:
        """
        Deactivate the plugin.
        
        Returns:
            bool: True if deactivated successfully
        """
        if self.status == PluginStatus.ACTIVE:
            self.set_status(PluginStatus.INACTIVE)
            return True
        return False
        
    # Event Hooks (optional overrides)
    
    def on_before_response(self, user_input: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Called before generating a response.
        
        Args:
            user_input: User's input
            context: Context dictionary
            
        Returns:
            Optional[str]: Modified input or None to proceed normally
        """
        return None
        
    def on_after_response(self, response: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Called after generating a response.
        
        Args:
            response: Generated response
            context: Context dictionary
            
        Returns:
            Optional[str]: Modified response or None to proceed normally
        """
        return None
        
    def on_conversation_start(self, user_id: str, context: Dict[str, Any]) -> None:
        """
        Called when a conversation starts.
        
        Args:
            user_id: User identifier
            context: Context dictionary
        """
        pass
        
    def on_conversation_end(self, user_id: str, context: Dict[str, Any]) -> None:
        """
        Called when a conversation ends.
        
        Args:
            user_id: User identifier
            context: Context dictionary
        """
        pass
        
    def on_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Called when an error occurs.
        
        Args:
            error: Exception that occurred
            context: Context dictionary
            
        Returns:
            bool: True if error was handled, False otherwise
        """
        return False
        
    # Helper methods
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
        
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
        
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(message)
        
    def __str__(self) -> str:
        """String representation."""
        if self.metadata:
            return f"Plugin({self.metadata.name} v{self.metadata.version})"
        return f"Plugin({self.__class__.__name__})"
        
    def __repr__(self) -> str:
        """String representation."""
        return self.__str__()

