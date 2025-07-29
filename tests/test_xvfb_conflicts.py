#!/usr/bin/env python3
"""
Test for potential Xvfb display conflicts in multiple concurrent sessions.
"""

import subprocess
import time
import signal
import os
from pathlib import Path

def test_xvfb_display_conflicts():
    """Test if multiple Xvfb sessions cause display number conflicts."""
    
    print("🧪 Testing Xvfb Display Conflicts")
    print("=" * 50)
    
    # Test direct Xvfb commands to see how display numbers are handled
    print("\n1. Testing direct Xvfb commands...")
    
    # Start a few Xvfb processes manually to see display assignment
    xvfb_processes = []
    
    for i in range(3):
        print(f"\n🖥️ Starting Xvfb session {i+1}...")
        
        # Let Xvfb choose display automatically (no explicit display number)
        cmd = [
            'Xvfb', 
            '+extension', 'Composite',
            '-screen', '0', '1280x800x24+32',
            '-nolisten', 'tcp',
            '-noreset',
            '+extension', 'GLX'
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            xvfb_processes.append(process)
            print(f"   Started Xvfb PID: {process.pid}")
            
            # Give it a moment to start
            time.sleep(0.5)
            
            # Check if it's still running
            if process.poll() is None:
                print(f"   ✅ Xvfb {i+1} running successfully")
            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ Xvfb {i+1} failed:")
                if stderr:
                    print(f"      Error: {stderr.decode()}")
                    
        except Exception as e:
            print(f"   ❌ Failed to start Xvfb {i+1}: {e}")
    
    print(f"\n📊 Started {len([p for p in xvfb_processes if p.poll() is None])} Xvfb processes")
    
    # Check for running displays
    print("\n2. Checking active X displays...")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        xvfb_lines = [line for line in result.stdout.split('\n') if 'Xvfb' in line]
        
        for line in xvfb_lines:
            print(f"   {line}")
            
        # Extract display numbers from command lines
        displays = []
        for line in xvfb_lines:
            parts = line.split()
            for i, part in enumerate(parts):
                if part.startswith(':') and part[1:].isdigit():
                    displays.append(part)
                    
        if displays:
            print(f"\n📺 Active displays: {displays}")
            if len(set(displays)) != len(displays):
                print("⚠️  WARNING: Duplicate display numbers detected!")
            else:
                print("✅ All displays have unique numbers")
        else:
            print("🔍 No explicit display numbers found (auto-assigned)")
            
    except Exception as e:
        print(f"❌ Error checking displays: {e}")
    
    # Test with explicit display numbers (potential conflict scenario)
    print("\n3. Testing explicit display number conflicts...")
    
    conflict_processes = []
    test_display = ":99"  # Use a high number unlikely to be in use
    
    for i in range(2):
        print(f"\n🎯 Attempting to start Xvfb on display {test_display} (attempt {i+1})...")
        
        cmd = ['Xvfb', test_display, '-screen', '0', '800x600x24']
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            conflict_processes.append(process)
            
            time.sleep(0.5)
            
            if process.poll() is None:
                print(f"   ✅ Started successfully on {test_display}")
            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ Failed to start on {test_display}")
                if stderr:
                    error_msg = stderr.decode().strip()
                    if "already in use" in error_msg or "Address already in use" in error_msg:
                        print(f"      Conflict detected: {error_msg}")
                    else:
                        print(f"      Other error: {error_msg}")
                        
        except Exception as e:
            print(f"   ❌ Exception starting Xvfb: {e}")
    
    # Test Xpra's display management
    print("\n4. Testing Xpra display management...")
    
    print("   Checking how Xpra handles display assignment...")
    
    # Create temporary session directories
    test_ports = [45001, 45002]
    xpra_processes = []
    
    for port in test_ports:
        session_dir = Path.home() / '.firefox-launcher' / 'test-sessions' / f'session-{port}'
        session_dir.mkdir(parents=True, exist_ok=True)
        
        for subdir in ['sockets', 'runtime', 'profile', 'temp']:
            (session_dir / subdir).mkdir(exist_ok=True)
        
        # Set permissions
        (session_dir / 'runtime').chmod(0o700)
        
        firefox_script = '/home/bdx/allcode/github/vantagecompute/jfl/scripts/firefox-xstartup'
        
        print(f"\n🚀 Testing Xpra on port {port}...")
        
        cmd = [
            'xpra', 'start',
            f'--bind-tcp=127.0.0.1:{port}',
            '--bind=none',
            '--html=on',
            '--daemon=no',
            '--exit-with-children=yes',
            f'--start-child={firefox_script}',
            '--xvfb=Xvfb +extension Composite -screen 0 800x600x24+32 -nolisten tcp -noreset +extension GLX',
            '--use-display=no'  # Force new display
        ]
        
        try:
            # Set environment for the session
            env = os.environ.copy()
            env.update({
                'XDG_RUNTIME_DIR': str(session_dir / 'runtime'),
                'TMPDIR': str(session_dir / 'temp'),
                'FIREFOX_PROFILE_DIR': str(session_dir / 'profile'),
                'PORT': str(port)
            })
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            xpra_processes.append((port, process))
            
            time.sleep(2)  # Give more time for Xpra startup
            
            if process.poll() is None:
                print(f"   ✅ Xpra started on port {port}")
                
                # Try to detect which display it's using
                try:
                    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if f':{port}' in line or str(process.pid) in line:
                            if 'Xvfb' in line:
                                print(f"      Xvfb command: {line.strip()}")
                except Exception:
                    pass
                    
            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ Xpra failed on port {port}")
                if stderr:
                    print(f"      Error: {stderr.decode()[:200]}...")
                    
        except Exception as e:
            print(f"   ❌ Exception with Xpra on port {port}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Xvfb processes: {len([p for p in xvfb_processes if p.poll() is None])}")
    print(f"   Xpra processes: {len([p for port, p in xpra_processes if p.poll() is None])}")
    
    # Cleanup
    print("\n🧹 Cleaning up test processes...")
    
    for process in xvfb_processes + conflict_processes:
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=2)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
    
    for port, process in xpra_processes:
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=3)
        except Exception:
            try:
                process.kill()
            except Exception:
                pass
    
    # Clean up test directories
    test_sessions_dir = Path.home() / '.firefox-launcher' / 'test-sessions'
    if test_sessions_dir.exists():
        import shutil
        shutil.rmtree(test_sessions_dir)
        print("   ✅ Cleaned up test session directories")
    
    print("✅ Test completed!")

if __name__ == "__main__":
    test_xvfb_display_conflicts()
