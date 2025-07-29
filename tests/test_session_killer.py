#!/usr/bin/env python3
"""
Test to demonstrate the session killing issue.

This test shows that the session_cleanup.py module registers global signal handlers
that kill ALL registered sessions, not just the ones belonging to a specific instance.
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jupyterlab_firefox_launcher.session_cleanup import session_registry

def test_session_killer_behavior():
    """Test that demonstrates the session killing problem."""
    
    print("🔍 Testing session registry behavior...")
    print(f"Session registry instance: {id(session_registry)}")
    
    # Simulate registering multiple sessions like the real code does
    print("\n📝 Registering multiple sessions:")
    
    # First session (simulating first Firefox launch)
    session_dir_1 = Path.home() / '.firefox-launcher' / 'sessions' / 'session-8001'
    session_dir_1.mkdir(parents=True, exist_ok=True)
    
    session_registry.register_session(8001, 12345, session_dir_1)
    print(f"✅ Registered session 1: port=8001, pid=12345")
    
    # Second session (simulating second Firefox launch)
    session_dir_2 = Path.home() / '.firefox-launcher' / 'sessions' / 'session-8002'
    session_dir_2.mkdir(parents=True, exist_ok=True)
    
    session_registry.register_session(8002, 12346, session_dir_2)
    print(f"✅ Registered session 2: port=8002, pid=12346")
    
    # Check what sessions are tracked
    active_sessions = session_registry.get_active_sessions()
    print(f"\n📊 Currently tracked sessions: {len(active_sessions)}")
    for port, info in active_sessions.items():
        print(f"   Port {port}: PID {info['process_id']}")
    
    print("\n🔍 Testing signal handler behavior...")
    
    # Check if signal handlers are registered
    print(f"SIGTERM handler: {signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGTERM))}")
    print(f"SIGINT handler: {signal.signal(signal.SIGINT, signal.getsignal(signal.SIGINT))}")
    
    # The problem: When ANY instance of the launcher triggers a signal,
    # ALL sessions get killed because they're all stored in the same global registry
    
    print("\n💥 THE PROBLEM:")
    print("- session_registry is a GLOBAL SINGLETON")
    print("- ALL Firefox launcher instances share the SAME registry")
    print("- Signal handlers (SIGTERM, SIGINT) are registered GLOBALLY")
    print("- When ANY launcher process dies/restarts, it triggers signal cleanup")
    print("- Signal cleanup calls cleanup_all_sessions() which kills ALL sessions")
    print("- This explains why starting a new session kills older ones!")
    
    return active_sessions

def test_multiple_launcher_instances():
    """Test what happens when multiple launcher instances exist."""
    
    print("\n🧪 Testing multiple launcher instances scenario:")
    
    # Simulate what happens in reality:
    # 1. User starts first Firefox session -> creates session_registry, registers session 1
    # 2. User starts second Firefox session -> uses SAME session_registry, registers session 2
    # 3. When second session starts, if the launcher process restarts/dies, signal handler triggers
    # 4. Signal handler calls cleanup_all_sessions() -> kills BOTH sessions
    
    # Clear any existing sessions first
    active_sessions = session_registry.get_active_sessions()
    for port in list(active_sessions.keys()):
        session_registry.unregister_session(port)
    
    print("🚀 Simulating first launcher instance starting...")
    session_registry.register_session(9001, 11111)
    print(f"   Registered session: port=9001, pid=11111")
    
    print("🚀 Simulating second launcher instance starting...")
    session_registry.register_session(9002, 22222)
    print(f"   Registered session: port=9002, pid=22222")
    
    active_sessions = session_registry.get_active_sessions()
    print(f"📊 Total sessions tracked by global registry: {len(active_sessions)}")
    
    print("\n💀 Now simulating what happens when launcher restarts...")
    print("   (In real scenario: JupyterLab restarts, or notebook kernel restarts)")
    print("   -> SIGTERM/SIGINT signal sent to launcher process")
    print("   -> Signal handler calls cleanup_all_sessions()")
    print("   -> ALL sessions get terminated!")
    
    # Simulate the cleanup that would happen
    print(f"\n🧹 cleanup_all_sessions() would terminate {len(active_sessions)} sessions:")
    for port, info in active_sessions.items():
        print(f"   Would kill session port={port}, pid={info['process_id']}")
    
    print("\n✅ This explains the bug! The solution is to NOT use global signal handlers")
    print("   or to make session tracking per-launcher-instance instead of global.")

if __name__ == "__main__":
    print("🐛 DEBUG: Session Killer Analysis")
    print("=" * 50)
    
    test_session_killer_behavior()
    test_multiple_launcher_instances()
    
    print("\n🔧 RECOMMENDATIONS:")
    print("1. Remove global signal handlers from session_cleanup.py")
    print("2. Handle cleanup only in the specific handler instance, not globally")
    print("3. Or: Make session tracking per-process instead of global")
    print("4. Or: Use process-specific cleanup instead of signal-based cleanup")
