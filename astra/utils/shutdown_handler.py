#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ASTRA - Graceful Shutdown Handler
Manages proper cleanup of resources during application shutdown.
"""

import signal
import sys
import threading
import logging
import atexit
from typing import Callable, List, Optional
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class ShutdownHandler:
    """
    Handles graceful shutdown of the ASTRA application.
    
    Manages:
    - Signal handling (SIGTERM, SIGINT)
    - Resource cleanup callbacks
    - Thread termination
    - Temporary file cleanup
    - State persistence
    """
    
    def __init__(self):
        """Initialize the shutdown handler."""
        self._shutdown_callbacks: List[Callable[[], None]] = []
        self._shutdown_in_progress = False
        self._shutdown_lock = threading.Lock()
        self._temp_files: List[Path] = []
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        # Register atexit handler as last resort
        atexit.register(self._atexit_handler)
        
        logger.info("🛡️ Shutdown handler initialized")
    
    def register_callback(self, callback: Callable[[], None], name: Optional[str] = None):
        """
        Register a callback to be called during shutdown.
        
        Args:
            callback: Function to call during shutdown
            name: Optional name for the callback (for logging)
        """
        if name:
            # Wrap callback to add logging
            original_callback = callback
            def named_callback():
                try:
                    logger.info(f"🔄 Executing shutdown callback: {name}")
                    original_callback()
                    logger.info(f"✅ Completed shutdown callback: {name}")
                except Exception as e:
                    logger.error(f"❌ Error in shutdown callback {name}: {e}")
            callback = named_callback
        
        self._shutdown_callbacks.append(callback)
        logger.debug(f"Registered shutdown callback: {name or 'unnamed'}")
    
    def register_temp_file(self, file_path: Path):
        """
        Register a temporary file for cleanup during shutdown.
        
        Args:
            file_path: Path to temporary file
        """
        self._temp_files.append(file_path)
        logger.debug(f"Registered temp file for cleanup: {file_path}")
    
    def _handle_signal(self, signum, frame):
        """
        Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = signal.Signals(signum).name
        logger.info(f"🛑 Received signal: {signal_name}")
        
        # Perform graceful shutdown
        self.shutdown()
        
        # Exit with appropriate code
        sys.exit(0)
    
    def _atexit_handler(self):
        """Handle atexit callback."""
        if not self._shutdown_in_progress:
            logger.info("🔄 atexit handler triggered")
            self.shutdown()
    
    def shutdown(self, timeout: float = 30.0):
        """
        Perform graceful shutdown.
        
        Args:
            timeout: Maximum time to wait for shutdown (seconds)
        """
        with self._shutdown_lock:
            if self._shutdown_in_progress:
                logger.warning("Shutdown already in progress")
                return
            
            self._shutdown_in_progress = True
        
        logger.info("=" * 60)
        logger.info("🛑 ASTRA GRACEFUL SHUTDOWN INITIATED")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Execute callbacks in reverse order (LIFO)
        for i, callback in enumerate(reversed(self._shutdown_callbacks)):
            if time.time() - start_time > timeout:
                logger.warning(f"Shutdown timeout reached, {len(self._shutdown_callbacks) - i} callbacks remaining")
                break
            
            try:
                callback()
            except Exception as e:
                logger.error(f"Error during shutdown callback: {e}", exc_info=True)
        
        # Clean up temporary files
        self._cleanup_temp_files()
        
        # Log active threads
        self._log_active_threads()
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Shutdown completed in {elapsed:.2f} seconds")
        logger.info("=" * 60)
    
    def _cleanup_temp_files(self):
        """Clean up registered temporary files."""
        if not self._temp_files:
            return
        
        logger.info(f"🧹 Cleaning up {len(self._temp_files)} temporary files")
        
        for file_path in self._temp_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Deleted temp file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete temp file {file_path}: {e}")
    
    def _log_active_threads(self):
        """Log information about active threads."""
        active_threads = threading.enumerate()
        if len(active_threads) > 1:  # More than just main thread
            logger.info(f"⚠️ {len(active_threads)} threads still active:")
            for thread in active_threads:
                logger.info(f"  - {thread.name} (daemon={thread.daemon}, alive={thread.is_alive()})")
        else:
            logger.info("✅ All threads terminated successfully")


# Global shutdown handler instance
_shutdown_handler: Optional[ShutdownHandler] = None


def get_shutdown_handler() -> ShutdownHandler:
    """
    Get global shutdown handler instance (singleton).
    
    Returns:
        ShutdownHandler instance
    """
    global _shutdown_handler
    if _shutdown_handler is None:
        _shutdown_handler = ShutdownHandler()
    return _shutdown_handler


def register_shutdown_callback(callback: Callable[[], None], name: Optional[str] = None):
    """
    Register a callback to be called during shutdown.
    
    Args:
        callback: Function to call during shutdown
        name: Optional name for the callback
    """
    get_shutdown_handler().register_callback(callback, name)


def register_temp_file(file_path: Path):
    """
    Register a temporary file for cleanup.
    
    Args:
        file_path: Path to temporary file
    """
    get_shutdown_handler().register_temp_file(file_path)


def shutdown_now(timeout: float = 30.0):
    """
    Trigger immediate graceful shutdown.
    
    Args:
        timeout: Maximum time to wait for shutdown
    """
    get_shutdown_handler().shutdown(timeout)


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get handler
    handler = get_shutdown_handler()
    
    # Register some test callbacks
    def cleanup_1():
        print("Cleanup 1: Closing database connection")
        time.sleep(0.5)
    
    def cleanup_2():
        print("Cleanup 2: Saving state")
        time.sleep(0.3)
    
    def cleanup_3():
        print("Cleanup 3: Stopping threads")
        time.sleep(0.2)
    
    handler.register_callback(cleanup_1, "database_cleanup")
    handler.register_callback(cleanup_2, "state_save")
    handler.register_callback(cleanup_3, "thread_stop")
    
    # Create a temp file
    import tempfile
    temp_file = Path(tempfile.mktemp())
    temp_file.write_text("test")
    handler.register_temp_file(temp_file)
    
    print("Shutdown handler test - Press Ctrl+C to test graceful shutdown")
    print("Waiting for signal...")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt caught, shutdown handler will execute")
