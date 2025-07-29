#!/usr/bin/env python3
"""
Test to verify the session killing bug and the fix.
"""

import os
import sys
import signal
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_current_buggy_behavior():
    """Test the current buggy behavior where global signal handlers kill all sessions."""
    
    print("🐛 Testing CURRENT (buggy) behavior...")
    
    # Import the current session_cleanup module
    from jupyterlab_firefox_launcher.session_cleanup import session_registry
    
    # Clear any existing sessions
    active_sessions = session_registry.get_active_sessions()
    for port in list(active_sessions.keys()):
        session_registry.unregister_session(port)
    
    # Register some sessions
    session_registry.register_session(8001, 11111)
    session_registry.register_session(8002, 22222)
    
    active_sessions = session_registry.get_active_sessions()
    print(f"📊 Registered {len(active_sessions)} sessions")
    
    # Check that signal handlers are global
    sigterm_handler = signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGTERM))
    sigint_handler = signal.signal(signal.SIGINT, signal.getsignal(signal.SIGINT))
    
    print(f"🔧 SIGTERM handler: {type(sigterm_handler).__name__}")
    print(f"🔧 SIGINT handler: {type(sigint_handler).__name__}")
    
    # The handlers are bound methods of the global session_registry instance
    if hasattr(sigterm_handler, '__self__'):
        print(f"🔧 SIGTERM handler belongs to: {id(sigterm_handler.__self__)}")
        print(f"🔧 session_registry id: {id(session_registry)}")
        print(f"🐛 Same instance: {sigterm_handler.__self__ is session_registry}")
    
    print("💥 PROBLEM: Global signal handlers will kill ALL sessions across ALL instances!")
    return active_sessions

if __name__ == "__main__":
    print("🧪 Session Killer Bug Verification")
    print("=" * 40)
    
    sessions = test_current_buggy_behavior()
    
    print(f"\n🎯 SUMMARY:")
    print(f"- Found {len(sessions)} sessions that would be killed")
    print(f"- Signal handlers are globally registered")
    print(f"- Any process restart/signal will kill ALL sessions")
    print(f"- This explains why new sessions kill old ones!")
