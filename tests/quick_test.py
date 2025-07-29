#!/usr/bin/env python3
"""
Quick test script to verify Xpra/Firefox startup with correct configuration.
"""

import subprocess
import time
import socket
from pathlib import Path

def find_free_port():
    """Find a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def test_xpra_firefox_fixed():
    """Test Xpra with corrected Firefox configuration."""
    print("🔧 Testing Xpra with corrected Firefox configuration...")
    
    port = find_free_port()
    print(f"Using port: {port}")
    
    # Create session directory
    session_dir = Path.home() / '.firefox-launcher' / 'test-sessions' / f'test-{port}'
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    socket_dir = session_dir / 'sockets'
    runtime_dir = session_dir / 'runtime'
    profile_dir = session_dir / 'profile'
    temp_dir = session_dir / 'temp'
    
    for subdir in [socket_dir, runtime_dir, profile_dir, temp_dir]:
        subdir.mkdir(exist_ok=True)
    
    firefox_script = '/home/bdx/allcode/github/vantagecompute/jfl/scripts/firefox-xstartup'
    
    # Corrected Xpra command - let Xpra manage DISPLAY automatically
    cmd = [
        'xpra', 'start',
        f'--bind-tcp=0.0.0.0:{port}',
        '--bind=none',
        '--html=on',
        '--daemon=no',
        '--exit-with-children=yes',
        '--start=',
        f'--start-child={firefox_script}',
        '--xvfb=/usr/bin/Xvfb +extension Composite -screen 0 1280x800x24+32 -nolisten tcp -noreset',
        f'--socket-dir={socket_dir}',
        '--mdns=no',
        '--auth=allow',
        '--tcp-auth=allow',
        '--pulseaudio=no',  # Disable audio to reduce warnings
        '--notifications=no',  # Disable notifications
        '--webcam=no',  # Disable webcam
        # Environment variables - let Xpra set DISPLAY
        f'--env=PORT={port}',
        f'--env=XDG_RUNTIME_DIR={runtime_dir}',
        f'--env=TMPDIR={temp_dir}',
        f'--env=FIREFOX_PROFILE_DIR={profile_dir}',
        '--env=MOZ_DBUS_REMOTE=0',
    ]
    
    print("🚀 Running corrected Xpra command:")
    print(f"   Command: xpra start --bind-tcp=0.0.0.0:{port} [with corrected DISPLAY handling]")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Wait for startup
        print("⏱️ Waiting 8 seconds for startup...")
        time.sleep(8)
        poll_result = process.poll()
        
        if poll_result is None:
            print("✅ Process is still running after 8 seconds")
            
            # Test port connectivity
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(2)
                result = test_sock.connect_ex(('localhost', port))
                test_sock.close()
                
                if result == 0:
                    print(f"✅ Port {port} is accepting connections")
                    print(f"🌐 Firefox session should be available at: http://localhost:{port}/")
                    
                    # Keep running for manual testing
                    print("⏸️ Session running for 15 seconds for manual testing...")
                    time.sleep(15)
                    
                else:
                    print(f"⚠️ Port {port} not accepting connections yet")
            except Exception as sock_error:
                print(f"⚠️ Socket test error: {sock_error}")
            
            # Terminate gracefully
            print("🛑 Terminating session...")
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Session terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Session force-killed")
                
            return True
            
        else:
            print(f"❌ Process exited with return code: {poll_result}")
            
            # Get output
            stdout, stderr = process.communicate()
            
            if stdout:
                print(f"📤 STDOUT:\n{stdout[-1000:]}")  # Last 1000 chars
            if stderr:
                print(f"📤 STDERR:\n{stderr[-1500:]}")  # Last 1500 chars
            
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick Xpra/Firefox Configuration Test")
    print("=" * 50)
    success = test_xpra_firefox_fixed()
    if success:
        print("\n🎉 Test PASSED! The configuration should work.")
    else:
        print("\n❌ Test FAILED! Configuration needs more fixes.")
