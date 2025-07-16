#!/usr/bin/env python3
"""
Firefox Launcher Extension - Diagnostic Tool

Run this to diagnose server proxy issues:
    python -m jupyterlab_firefox_launcher
"""

import sys
import os
import subprocess
import importlib.util

def check_server_proxy_registration():
    """Check if the firefox-desktop server proxy is properly registered"""
    print("🔍 Checking server proxy registration...")
    
    try:
        # Try the modern way first
        try:
            from importlib.metadata import entry_points
            eps = entry_points()
            if hasattr(eps, 'select'):
                # Python 3.10+
                proxy_eps = eps.select(group='jupyter_serverproxy_servers')
            else:
                # Python 3.8-3.9
                proxy_eps = eps.get('jupyter_serverproxy_servers', [])
        except ImportError:
            # Fallback to pkg_resources
            import pkg_resources
            proxy_eps = pkg_resources.iter_entry_points('jupyter_serverproxy_servers')
        
        firefox_found = False
        print("📋 Registered server proxy endpoints:")
        
        for ep in proxy_eps:
            print(f"  • {ep.name}: {ep.value}")
            if ep.name == "firefox-desktop":
                firefox_found = True
                print("    ✅ Firefox desktop endpoint found!")
                
                # Try to load and test the function
                try:
                    func = ep.load()
                    config = func()
                    print(f"    ✅ Configuration loaded successfully")
                    print(f"    📋 Command: {config.get('command', 'N/A')[:80]}...")
                    return True
                except Exception as e:
                    print(f"    ❌ Error loading configuration: {e}")
                    return False
        
        if not firefox_found:
            print("❌ firefox-desktop endpoint NOT found in entry points")
            return False
            
    except Exception as e:
        print(f"❌ Error checking entry points: {e}")
        return False

def check_jupyter_server_config():
    """Check if Jupyter server recognizes the extension"""
    print("\n🔍 Checking Jupyter server configuration...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'jupyter', 'server', 'extension', 'list'
        ], capture_output=True, text=True, timeout=30)
        
        print("📋 Jupyter server extensions:")
        print(result.stdout)
        
        if 'jupyterlab_firefox_launcher' in result.stdout:
            print("✅ Firefox launcher extension is loaded by Jupyter server")
            return True
        else:
            print("❌ Firefox launcher extension NOT found in server extensions")
            return False
            
    except Exception as e:
        print(f"❌ Error checking server extensions: {e}")
        return False

def test_server_proxy_function():
    """Test the server proxy function directly"""
    print("\n🔍 Testing server proxy function...")
    
    try:
        from jupyterlab_firefox_launcher.server_proxy import setup_firefox_desktop
        config = setup_firefox_desktop()
        
        print("✅ Server proxy function works correctly")
        print(f"📋 Generated config keys: {list(config.keys())}")
        
        # Check command
        command = config.get('command', [])
        if command and 'xpra' in command[0]:
            print("✅ Xpra command configured correctly")
        else:
            print("❌ Xpra command not found or incorrect")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing server proxy function: {e}")
        return False

def check_system_dependencies():
    """Check system dependencies"""
    print("\n🔍 Checking system dependencies...")
    
    # Check Xpra
    try:
        result = subprocess.run(['xpra', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Xpra is available")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print("❌ Xpra not working properly")
    except Exception as e:
        print(f"❌ Xpra error: {e}")
    
    # Check Firefox
    try:
        result = subprocess.run(['firefox', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Firefox is available")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print("❌ Firefox not working properly")
    except Exception as e:
        print(f"❌ Firefox error: {e}")

def main():
    print("🔧 JupyterLab Firefox Launcher - Diagnostic Tool")
    print("=" * 60)
    
    # Run all checks
    checks = [
        check_server_proxy_registration(),
        check_jupyter_server_config(),
        test_server_proxy_function(),
    ]
    
    check_system_dependencies()
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    
    if all(checks):
        print("✅ All checks passed - extension should be working")
        print("\n🎯 Try these URLs:")
        print("   • In JupyterLab: Click the Firefox Desktop icon in the launcher")
        print("   • Direct URL: /firefox-desktop/ (relative to your server)")
        print("   • Full path: Check your JUPYTERHUB_SERVICE_PREFIX environment variable")
    else:
        print("❌ Some checks failed - see errors above")
        print("\n🔧 Possible fixes:")
        print("   • Restart Jupyter server/JupyterHub")
        print("   • Reinstall extension: pip install --force-reinstall jupyterlab-firefox-launcher")
        print("   • Check system dependencies: sudo apt install xpra firefox")

if __name__ == "__main__":
    main()