#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Lazy Import Helper
Provides lazy loading for optional dependencies to improve startup time.
"""

import logging
import importlib
from typing import Optional, Any, Dict, Callable
from functools import wraps
import sys

logger = logging.getLogger(__name__)


class LazyModule:
    """
    Lazy wrapper for module imports.
    
    The module is only imported when accessed for the first time.
    """
    
    def __init__(self, module_name: str, fallback: Any = None):
        """
        Initialize lazy module.
        
        Args:
            module_name: Full module name (e.g. 'numpy')
            fallback: Value to return if import fails
        """
        self._module_name = module_name
        self._module: Optional[Any] = None
        self._fallback = fallback
        self._import_attempted = False
    
    def _load_module(self):
        """Load the module (called on first access)."""
        if self._import_attempted:
            return
        
        self._import_attempted = True
        
        try:
            self._module = importlib.import_module(self._module_name)
            logger.debug(f"✅ Lazy loaded: {self._module_name}")
        except ImportError as e:
            logger.warning(f"⚠️ Failed to lazy load {self._module_name}: {e}")
            self._module = self._fallback
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from the module."""
        if self._module is None:
            self._load_module()
        
        if self._module is None:
            raise ImportError(f"Module {self._module_name} not available")
        
        return getattr(self._module, name)
    
    def __call__(self, *args, **kwargs) -> Any:
        """Allow calling the module if it's callable."""
        if self._module is None:
            self._load_module()
        
        if self._module is None:
            raise ImportError(f"Module {self._module_name} not available")
        
        return self._module(*args, **kwargs)
    
    @property
    def is_available(self) -> bool:
        """Check if module is available."""
        if not self._import_attempted:
            self._load_module()
        return self._module is not None


class LazyImportManager:
    """
    Manages lazy imports with caching and dependency checking.
    """
    
    def __init__(self):
        self._modules: Dict[str, LazyModule] = {}
        self._availability_cache: Dict[str, bool] = {}
    
    def register(self, module_name: str, fallback: Any = None) -> LazyModule:
        """
        Register a module for lazy loading.
        
        Args:
            module_name: Full module name
            fallback: Fallback value if import fails
            
        Returns:
            LazyModule instance
        """
        if module_name not in self._modules:
            self._modules[module_name] = LazyModule(module_name, fallback)
        return self._modules[module_name]
    
    def is_available(self, module_name: str) -> bool:
        """
        Check if a module is available.
        
        Args:
            module_name: Module name to check
            
        Returns:
            True if module can be imported
        """
        if module_name in self._availability_cache:
            return self._availability_cache[module_name]
        
        try:
            importlib.import_module(module_name)
            self._availability_cache[module_name] = True
            return True
        except ImportError:
            self._availability_cache[module_name] = False
            return False
    
    def get_module(self, module_name: str, fallback: Any = None) -> LazyModule:
        """
        Get or register a lazy module.
        
        Args:
            module_name: Module name
            fallback: Fallback value
            
        Returns:
            LazyModule instance
        """
        return self.register(module_name, fallback)
    
    def preload(self, *module_names: str):
        """
        Preload modules (useful for critical dependencies).
        
        Args:
            *module_names: Module names to preload
        """
        for module_name in module_names:
            if module_name in self._modules:
                self._modules[module_name]._load_module()
            else:
                self.register(module_name)._load_module()
    
    def get_status(self) -> Dict[str, bool]:
        """
        Get status of all registered modules.
        
        Returns:
            Dictionary with module availability
        """
        status = {}
        for name, module in self._modules.items():
            status[name] = module.is_available
        return status


# Global lazy import manager
_lazy_import_manager = LazyImportManager()


def lazy_import(module_name: str, fallback: Any = None) -> LazyModule:
    """
    Import a module lazily.
    
    Args:
        module_name: Full module name
        fallback: Fallback value if import fails
        
    Returns:
        LazyModule instance
        
    Example:
        numpy = lazy_import('numpy')
        # numpy is not imported yet
        
        arr = numpy.array([1, 2, 3])  # Now it's imported
    """
    return _lazy_import_manager.register(module_name, fallback)


def requires(*module_names: str):
    """
    Decorator to specify module requirements for a function.
    
    Args:
        *module_names: Required module names
        
    Raises:
        ImportError: If required modules are not available
        
    Example:
        @requires('numpy', 'pandas')
        def process_data(data):
            import numpy as np
            import pandas as pd
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check all requirements
            missing = []
            for module_name in module_names:
                if not _lazy_import_manager.is_available(module_name):
                    missing.append(module_name)
            
            if missing:
                raise ImportError(
                    f"Function {func.__name__} requires: {', '.join(missing)}\n"
                    f"Install with: pip install {' '.join(missing)}"
                )
            
            return func(*args, **kwargs)
        
        # Store requirements for introspection
        wrapper.__requirements__ = module_names
        
        return wrapper
    return decorator


def optional_import(module_name: str, fallback_value: Any = None) -> tuple[Any, bool]:
    """
    Try to import a module, return fallback if not available.
    
    Args:
        module_name: Module to import
        fallback_value: Value to return if import fails
        
    Returns:
        Tuple of (module or fallback, success flag)
        
    Example:
        numpy, numpy_available = optional_import('numpy')
        if numpy_available:
            arr = numpy.array([1, 2, 3])
    """
    try:
        module = importlib.import_module(module_name)
        return module, True
    except ImportError as e:
        logger.debug(f"Optional import failed: {module_name} - {e}")
        return fallback_value, False


def check_dependencies(*module_names: str) -> Dict[str, bool]:
    """
    Check availability of multiple modules.
    
    Args:
        *module_names: Module names to check
        
    Returns:
        Dictionary mapping module names to availability
        
    Example:
        deps = check_dependencies('numpy', 'pandas', 'sklearn')
        if not all(deps.values()):
            print(f"Missing: {[k for k, v in deps.items() if not v]}")
    """
    return {
        name: _lazy_import_manager.is_available(name)
        for name in module_names
    }


def get_import_status() -> Dict[str, bool]:
    """
    Get status of all registered lazy imports.
    
    Returns:
        Dictionary with module availability
    """
    return _lazy_import_manager.get_status()


def preload_modules(*module_names: str):
    """
    Preload critical modules at startup.
    
    Args:
        *module_names: Module names to preload
    """
    _lazy_import_manager.preload(*module_names)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("=== Testing Lazy Import System ===\n")
    
    # Test 1: Lazy import of standard library
    print("1. Testing lazy import of 'json':")
    json_module = lazy_import('json')
    print(f"   Module registered: {json_module is not None}")
    print(f"   Is available: {json_module.is_available}")
    data = json_module.dumps({"test": "value"})
    print(f"   Used module: {data}")
    
    # Test 2: Lazy import with fallback
    print("\n2. Testing lazy import with fallback (non-existent module):")
    fake_module = lazy_import('nonexistent_module_xyz', fallback=None)
    print(f"   Module registered: {fake_module is not None}")
    print(f"   Is available: {fake_module.is_available}")
    
    # Test 3: Optional import
    print("\n3. Testing optional import:")
    os_module, available = optional_import('os')
    print(f"   'os' available: {available}")
    if available:
        print(f"   Current directory: {os_module.getcwd()}")
    
    # Test 4: Check dependencies
    print("\n4. Testing dependency check:")
    deps = check_dependencies('sys', 'os', 'fake_module', 'logging')
    for name, available in deps.items():
        status = "✅" if available else "❌"
        print(f"   {status} {name}: {available}")
    
    # Test 5: Decorator
    print("\n5. Testing @requires decorator:")
    
    @requires('os', 'sys')
    def system_info():
        import os
        import sys
        return f"Python {sys.version_info.major}.{sys.version_info.minor} on {os.name}"
    
    try:
        info = system_info()
        print(f"   System info: {info}")
    except ImportError as e:
        print(f"   Error: {e}")
    
    # Test 6: Import status
    print("\n6. Registered lazy imports:")
    status = get_import_status()
    for name, available in status.items():
        status_icon = "✅" if available else "❌"
        print(f"   {status_icon} {name}")
    
    print("\n✅ All tests completed!")
