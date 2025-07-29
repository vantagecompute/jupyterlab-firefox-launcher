# Copyright (c) 2025 Vantage Compute Corporation.
"""
Session cleanup system for Firefox launcher extension.

This module provides cleanup functionality to ensure all Xpra/Firefox sessions
are properly terminated when the notebook server is shutdown or culled.
"""

import os
import sys
import signal
import atexit
import logging
import threading
import time
import shutil
from pathlib import Path
from typing import Dict, List, Set, Any

import psutil

# Set up logger for cleanup operations
_logger = logging.getLogger(__name__)


class FirefoxSessionRegistry:
    """Centralized registry for tracking active Firefox/Xpra sessions."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one registry exists."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._sessions: Dict[int, Dict[str, Any]] = {}  # port -> session_info
        self._session_lock = threading.Lock()
        self._cleanup_registered = False
        self._initialized = True
        
    def register_session(self, port: int, process_id: int, session_dir: Path = None):
        """Register a new Firefox/Xpra session for cleanup tracking."""
        with self._session_lock:
            self._sessions[port] = {
                'process_id': process_id,
                'port': port,
                'session_dir': session_dir,
                'registered_at': time.time()
            }
            _logger.info(f"📝 Registered session for cleanup: port={port}, pid={process_id}")
            
            # Register cleanup handlers on first session
            if not self._cleanup_registered:
                self._register_cleanup_handlers()
                self._cleanup_registered = True
                
    def unregister_session(self, port: int):
        """Remove a session from cleanup tracking."""
        with self._session_lock:
            if port in self._sessions:
                session_info = self._sessions.pop(port)
                _logger.info(f"📝 Unregistered session from cleanup: port={port}, pid={session_info.get('process_id')}")
                
    def get_active_sessions(self) -> Dict[int, Dict[str, Any]]:
        """Get a copy of all currently tracked sessions."""
        with self._session_lock:
            return dict(self._sessions)
            
    def cleanup_all_sessions(self, force: bool = False):
        """Clean up all registered sessions."""
        with self._session_lock:
            sessions_to_clean = list(self._sessions.items())
            
        if not sessions_to_clean:
            _logger.info("🧹 No active sessions to clean up")
            return 0
            
        _logger.info(f"🧹 Server shutdown cleanup: {len(sessions_to_clean)} active sessions (force={force})")
        cleaned = 0
        
        for port, session_info in sessions_to_clean:
            try:
                process_id = session_info['process_id']
                session_dir = session_info.get('session_dir')
                
                # Terminate process and children
                if self._terminate_process_tree(process_id, force):
                    cleaned += 1
                    
                # Clean up session directory
                if session_dir and session_dir.exists():
                    try:
                        shutil.rmtree(session_dir)
                        _logger.info(f"🗑️ Removed session directory: {session_dir}")
                    except Exception as dir_error:
                        _logger.warning(f"⚠️ Failed to remove session directory {session_dir}: {dir_error}")
                        
                # Remove from tracking
                self.unregister_session(port)
                
            except Exception as session_error:
                _logger.error(f"❌ Error cleaning up session on port {port}: {session_error}")
                
        _logger.info(f"✅ Server shutdown cleanup completed: {cleaned}/{len(sessions_to_clean)} sessions")
        return cleaned
        
    def _terminate_process_tree(self, process_id: int, force: bool = False) -> bool:
        """Terminate a process and all its children."""
        try:
            process = psutil.Process(process_id)
            process_name = process.name()
            
            # Get all child processes first
            children = process.children(recursive=True)
            _logger.info(f"🔥 Terminating process tree: PID {process_id} ({process_name}) + {len(children)} children")
            
            # Terminate children first
            for child in children:
                try:
                    child.terminate()
                    _logger.debug(f"   Terminated child: {child.pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            # Terminate main process
            process.terminate()
            
            # Wait for graceful termination
            timeout = 3 if not force else 1
            try:
                process.wait(timeout=timeout)
                _logger.info(f"✅ Process {process_id} terminated gracefully")
                return True
            except psutil.TimeoutExpired:
                if force:
                    # Force kill if needed
                    _logger.warning(f"⏰ Force killing unresponsive process {process_id}")
                    process.kill()
                    for child in children:
                        try:
                            child.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    return True
                else:
                    _logger.warning(f"⏰ Process {process_id} didn't terminate in {timeout}s")
                    return False
                    
        except psutil.NoSuchProcess:
            _logger.info(f"⚠️ Process {process_id} already terminated")
            return True
        except Exception as term_error:
            _logger.error(f"❌ Error terminating process {process_id}: {term_error}")
            return False
            
    def _register_cleanup_handlers(self):
        """Register cleanup handlers for various shutdown scenarios."""
        _logger.info("🔧 Registering cleanup handlers for server shutdown")
        
        # Register atexit handler
        atexit.register(self._atexit_cleanup)
        
        # Register signal handlers
        try:
            signal.signal(signal.SIGTERM, self._signal_cleanup)
            signal.signal(signal.SIGINT, self._signal_cleanup)
            _logger.info("✅ Signal handlers registered (SIGTERM, SIGINT)")
        except Exception as signal_error:
            _logger.warning(f"⚠️ Could not register signal handlers: {signal_error}")
        
        # Try to register with Jupyter server hooks
        try:
            self._register_jupyter_hooks()
        except Exception as jupyter_error:
            _logger.warning(f"⚠️ Could not register Jupyter server hooks: {jupyter_error}")
            
        # Create PID file for external cleanup
        try:
            self._create_pid_file()
        except Exception as pid_error:
            _logger.warning(f"⚠️ Could not create PID file: {pid_error}")
        
        _logger.info("✅ Cleanup handlers registration completed")
        
    def _register_jupyter_hooks(self):
        """Register cleanup with Jupyter server if available."""
        try:
            from jupyter_server.serverapp import ServerApp
            from jupyter_core.application import JupyterApp
            
            # Get the current server app instance
            app_instance = None
            if hasattr(JupyterApp, 'instance'):
                app_instance = JupyterApp.instance()
                
            if app_instance and hasattr(app_instance, 'add_hook'):
                # Register shutdown hook with Jupyter server
                app_instance.add_hook('shutdown', lambda: self.cleanup_all_sessions(force=True))
                _logger.info("✅ Registered cleanup with Jupyter server shutdown hooks")
                return True
            else:
                _logger.debug("No Jupyter server app instance available for hooks")
                return False
                
        except ImportError:
            _logger.debug("Jupyter server not available for hook registration")
            return False
            
    def _create_pid_file(self):
        """Create a PID file to help external cleanup scripts."""
        pid_file = Path.home() / '.firefox-launcher' / 'jupyter_server.pid'
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
        _logger.info(f"📄 Created PID file: {pid_file}")
        
        # Register cleanup for PID file
        def cleanup_pid_file():
            try:
                if pid_file.exists():
                    pid_file.unlink()
                    _logger.debug(f"🗑️ Removed PID file: {pid_file}")
            except Exception as pid_error:
                _logger.warning(f"⚠️ Failed to remove PID file: {pid_error}")
                
        atexit.register(cleanup_pid_file)
        return pid_file
        
    def _atexit_cleanup(self):
        """Cleanup handler for normal Python exit."""
        _logger.info("🚪 atexit cleanup triggered - cleaning up all Firefox sessions")
        self.cleanup_all_sessions(force=True)
        
    def _signal_cleanup(self, signum, frame):
        """Cleanup handler for signal-based termination."""
        try:
            signal_name = signal.Signals(signum).name
        except:
            signal_name = str(signum)
            
        _logger.info(f"📡 Signal {signal_name} received - cleaning up all Firefox sessions")
        self.cleanup_all_sessions(force=True)
        
        # Re-raise the signal for normal termination
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)


# Create global session registry instance
session_registry = FirefoxSessionRegistry()
_logger.info("🏭 Firefox session cleanup system initialized")


def cleanup_firefox_profile(port: int) -> bool:
    """
    Clean up Firefox profile directory and session-specific directories for a given port.
    This is a wrapper around the existing cleanup function that also unregisters
    the session from the cleanup registry.
    
    Args:
        port: The port number of the Xpra process
    Returns:
        True if cleanup was successful or profile didn't exist, False otherwise
    """
    # Unregister from cleanup registry
    session_registry.unregister_session(port)
    
    # Import the existing cleanup function
    try:
        from . import firefox_handler
        return firefox_handler._cleanup_firefox_profile(port)
    except ImportError:
        # Fallback implementation
        try:
            home_dir = Path.home()
            session_dir = home_dir / '.firefox-launcher' / 'sessions' / f'session-{port}'
            if session_dir.exists():
                _logger.info(f"🧹 Cleaning up session directory: {session_dir}")
                shutil.rmtree(session_dir)
                _logger.info(f"✅ Successfully removed session directory: {session_dir}")
            return True
        except Exception as e:
            _logger.error(f"❌ Error cleaning up profile for port {port}: {e}")
            return False
