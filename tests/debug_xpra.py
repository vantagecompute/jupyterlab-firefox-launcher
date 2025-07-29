#!/usr/bin/env python3
"""
Debug script to test Xpra startup issues.
This script will test various Xpra configurations to help identify startup problems.
"""

import subprocess
import sys
import os
import tempfile
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

def test_xpra_basic():
    """Test basic Xpra functionality."""
    print("🔍 Testing basic Xpra functionality...")
    
    try:
        result = subprocess.run(['xpra', '--version'], capture_output=True, text=True, timeout=10)
        print(f"✅ Xpra version: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Xpra version check failed: {e}")
        return False

def test_xvfb():
    """Test if Xvfb is available."""
    print("🔍 Testing Xvfb availability...")
    
    try:
        result = subprocess.run(['which', 'Xvfb'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Xvfb found at: {result.stdout.strip()}")
            return True
        else:
            print("❌ Xvfb not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Xvfb check failed: {e}")
        return False

def test_firefox():
    """Test if Firefox is available."""
    print("🔍 Testing Firefox availability...")
    
    try:
        result = subprocess.run(['which', 'firefox'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Firefox found at: {result.stdout.strip()}")
            return True
        else:
            print("❌ Firefox not found in PATH")
            return False
    except Exception as e:
        print(f"❌ Firefox check failed: {e}")
        return False

def test_firefox_startup_script():
    """Test if firefox-xstartup script is available."""
    print("🔍 Testing firefox-xstartup script...")
    
    # Check in PATH first
    try:
        result = subprocess.run(['which', 'firefox-xstartup'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            script_path = result.stdout.strip()
            print(f"✅ firefox-xstartup found in PATH: {script_path}")
            
            # Check if executable
            if os.access(script_path, os.X_OK):
                print("✅ firefox-xstartup is executable")
                return script_path
            else:
                print("⚠️ firefox-xstartup is not executable")
                return script_path
        else:
            print("⚠️ firefox-xstartup not found in PATH")
    except Exception as e:
        print(f"❌ Error checking firefox-xstartup in PATH: {e}")
    
    # Check development location
    dev_path = Path(__file__).parent / 'scripts' / 'firefox-xstartup'
    if dev_path.exists():
        print(f"✅ firefox-xstartup found at development location: {dev_path}")
        if os.access(dev_path, os.X_OK):
            print("✅ firefox-xstartup is executable")
            return str(dev_path)
        else:
            print("⚠️ firefox-xstartup is not executable")
            return str(dev_path)
    else:
        print(f"❌ firefox-xstartup not found at development location: {dev_path}")
        return None

def test_minimal_xpra():
    """Test minimal Xpra start command."""
    print("🔍 Testing minimal Xpra start command...")
    
    port = find_free_port()
    print(f"Using port: {port}")
    
    # Create minimal session directory
    session_dir = Path.home() / '.firefox-launcher' / 'debug-sessions' / f'debug-{port}'
    session_dir.mkdir(parents=True, exist_ok=True)
    
    socket_dir = session_dir / 'sockets'
    socket_dir.mkdir(exist_ok=True)
    
    print(f"Session directory: {session_dir}")
    print(f"Socket directory: {socket_dir}")
    
    # Very minimal Xpra command
    cmd = [
        'xpra', 'start',
        f'--bind-tcp=0.0.0.0:{port}',
        '--bind=none',
        '--html=on',
        '--daemon=no',
        '--exit-with-children=yes',
        f'--socket-dir={socket_dir}',
        '--start=',  # No child process
        '--xvfb=/usr/bin/Xvfb +extension Composite -screen 0 1280x800x24+32 -nolisten tcp -noreset',
        '--mdns=no',
        '--auth=allow',
        '--tcp-auth=allow'
    ]
    
    print("🚀 Running minimal Xpra command:")
    print(f"   {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Wait a bit and check if process is still running
        time.sleep(2)
        poll_result = process.poll()
        
        if poll_result is None:
            print("✅ Process is still running after 2 seconds")
            
            # Try to connect to the port
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(1)
                result = test_sock.connect_ex(('localhost', port))
                test_sock.close()
                
                if result == 0:
                    print(f"✅ Port {port} is accepting connections")
                else:
                    print(f"⚠️ Port {port} is not yet accepting connections")
            except Exception as sock_error:
                print(f"⚠️ Socket test failed: {sock_error}")
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Process terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Process had to be force-killed")
            
            return True
            
        else:
            print(f"❌ Process exited immediately with return code: {poll_result}")
            
            # Capture output
            stdout, stderr = process.communicate()
            
            if stdout:
                print(f"📤 STDOUT:\n{stdout}")
            if stderr:
                print(f"📤 STDERR:\n{stderr}")
            
            return False
            
    except Exception as e:
        print(f"❌ Failed to start minimal Xpra: {e}")
        return False

def test_xpra_with_firefox():
    """Test Xpra with Firefox startup script."""
    print("🔍 Testing Xpra with Firefox startup script...")
    
    firefox_script = test_firefox_startup_script()
    if not firefox_script:
        print("❌ Cannot test with Firefox - startup script not available")
        return False
    
    port = find_free_port()
    print(f"Using port: {port}")
    
    # Create session directory
    session_dir = Path.home() / '.firefox-launcher' / 'debug-sessions' / f'firefox-debug-{port}'
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    socket_dir = session_dir / 'sockets'
    runtime_dir = session_dir / 'runtime'
    profile_dir = session_dir / 'profile'
    temp_dir = session_dir / 'temp'
    
    for subdir in [socket_dir, runtime_dir, profile_dir, temp_dir]:
        subdir.mkdir(exist_ok=True)
    
    print(f"Session structure created at: {session_dir}")
    
    # Xpra command with Firefox
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
        # Environment variables
        f'--env=DISPLAY=:{10 + port}',
        f'--env=PORT={port}',
        f'--env=XDG_RUNTIME_DIR={runtime_dir}',
        f'--env=TMPDIR={temp_dir}',
        f'--env=FIREFOX_PROFILE_DIR={profile_dir}',
        '--env=MOZ_DBUS_REMOTE=0',
    ]
    
    print("🚀 Running Xpra with Firefox:")
    print(f"   {' '.join(cmd[:10])}... (truncated)")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Process started with PID: {process.pid}")
        
        # Wait longer for Firefox startup
        print("⏱️ Waiting 5 seconds for Firefox startup...")
        time.sleep(5)
        poll_result = process.poll()
        
        if poll_result is None:
            print("✅ Process is still running after 5 seconds")
            
            # Try to connect to the port
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(2)
                result = test_sock.connect_ex(('localhost', port))
                test_sock.close()
                
                if result == 0:
                    print(f"✅ Port {port} is accepting connections")
                    print(f"🌐 You can test the session at: http://localhost:{port}/")
                else:
                    print(f"⚠️ Port {port} is not yet accepting connections")
            except Exception as sock_error:
                print(f"⚠️ Socket test failed: {sock_error}")
            
            # Keep running for a bit to allow manual testing
            print("⏸️ Keeping session running for 10 seconds for manual testing...")
            time.sleep(10)
            
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Process terminated cleanly")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Process had to be force-killed")
            
            return True
            
        else:
            print(f"❌ Process exited with return code: {poll_result}")
            
            # Capture output
            stdout, stderr = process.communicate()
            
            if stdout:
                print(f"📤 STDOUT:\n{stdout}")
            if stderr:
                print(f"📤 STDERR:\n{stderr}")
            
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Xpra with Firefox: {e}")
        return False

def main():
    """Run all debugging tests."""
    print("🔧 Firefox Launcher Xpra Debug Tool")
    print("=" * 50)
    
    results = []
    
    # Test basic dependencies
    results.append(("Xpra basic", test_xpra_basic()))
    results.append(("Xvfb available", test_xvfb()))
    results.append(("Firefox available", test_firefox()))
    results.append(("Firefox startup script", test_firefox_startup_script() is not None))
    
    print("\n" + "=" * 50)
    
    # Test Xpra startup
    results.append(("Minimal Xpra start", test_minimal_xpra()))
    
    print("\n" + "=" * 50)
    
    # Test with Firefox
    results.append(("Xpra with Firefox", test_xpra_with_firefox()))
    
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    failed_tests = [name for name, result in results if not result]
    if failed_tests:
        print(f"\n⚠️ Failed tests: {', '.join(failed_tests)}")
        print("   These issues need to be resolved for the Firefox launcher to work.")
    else:
        print("\n🎉 All tests passed! The Firefox launcher should work correctly.")

if __name__ == "__main__":
    main()
