#!/usr/bin/env python3
"""
Test concurrent Xpra sessions with the fixed command structure.
"""

import subprocess
import time
import socket
from pathlib import Path
import random

def test_concurrent_sessions():
    """Test multiple concurrent Xpra sessions with proper isolation."""
    
    print("🧪 Testing Concurrent Xpra Sessions with Fixed Commands")
    print("=" * 60)
    
    # Generate unique ports for testing
    ports = [random.randint(30000, 50000) for _ in range(3)]
    processes = []
    
    print(f"Testing with ports: {ports}")
    
    for i, port in enumerate(ports, 1):
        print(f"\n🚀 Starting session {i} on port {port}")
        
        # Create session directory (same as firefox_handler.py)
        session_dir = Path.home() / '.firefox-launcher' / 'sessions' / f'session-{port}'
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        socket_dir = session_dir / 'sockets'
        runtime_dir = session_dir / 'runtime' 
        profile_dir = session_dir / 'profile'
        temp_dir = session_dir / 'temp'
        
        for subdir in [socket_dir, runtime_dir, profile_dir, temp_dir]:
            subdir.mkdir(exist_ok=True)
        
        firefox_script = '/home/bdx/allcode/github/vantagecompute/jfl/scripts/firefox-xstartup'
        
        # Use the exact fixed command structure from firefox_handler.py
        cmd = [
            'xpra', 'start',
            f'--bind-tcp=0.0.0.0:{port}',
            '--bind=none',
            '--html=on',
            '--daemon=no',
            '--exit-with-children=yes',
            '--start-via-proxy=no',
            '--start=',
            f'--start-child={firefox_script}',
            # Fixed Xvfb configuration
            '--xvfb=/usr/bin/Xvfb +extension Composite -screen 0 1280x800x24+32 -nolisten tcp -noreset +extension GLX',
            '--mdns=no',
            '--pulseaudio=no',
            '--notifications=no',
            '--clipboard=yes',
            '--clipboard-direction=both',
            '--sharing=no',
            '--speaker=off',
            '--microphone=off',
            '--webcam=no',
            '--desktop-scaling=auto',
            '--resize-display=yes',
            '--cursors=yes',
            '--bell=no',
            '--system-tray=no',
            '--xsettings=yes',
            '--readonly=no',
            '--window-close=auto',
            '--dpi=96',
            '--compressors=lz4',  # Fixed compression syntax for v5.x
            '--quality=80',
            '--encoding=auto',
            '--min-quality=30',
            '--min-speed=30',
            '--auto-refresh-delay=0.15',
            '--fake-xinerama=auto',
            '--use-display=no',
        ]
        
        print(f"   Command: {' '.join(cmd[:5])}... [truncated]")
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=session_dir
            )
            processes.append((port, process))
            print(f"   Started with PID: {process.pid}")
            
            # Small delay between starts
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Failed to start: {e}")
    
    # Wait for sessions to initialize
    print(f"\n⏳ Waiting 5 seconds for sessions to initialize...")
    time.sleep(5)
    
    # Check session status
    print(f"\n📊 Checking session status:")
    successful_sessions = 0
    
    for port, process in processes:
        if process.poll() is None:
            print(f"   ✅ Port {port}: Running (PID {process.pid})")
            successful_sessions += 1
            
            # Test connectivity
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    print(f"      🌐 Port {port} accepting connections")
                else:
                    print(f"      ⚠️  Port {port} not accepting connections yet")
            except:
                print(f"      ❌ Port {port} connection test failed")
        else:
            return_code = process.returncode
            print(f"   ❌ Port {port}: Exited with code {return_code}")
            
            # Get error output
            stdout, stderr = process.communicate()
            if stderr:
                print(f"      Error: {stderr.strip()[:200]}...")
    
    print(f"\n🎯 Results: {successful_sessions}/{len(processes)} sessions running successfully")
    
    # Cleanup
    print(f"\n🧹 Cleaning up sessions...")
    for port, process in processes:
        if process.poll() is None:
            print(f"   Terminating session on port {port}")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"   Force killing session on port {port}")
                process.kill()
    
    return successful_sessions == len(processes)

if __name__ == "__main__":
    success = test_concurrent_sessions()
    print(f"\n{'✅ All sessions started successfully!' if success else '❌ Some sessions failed to start'}")
