#!/usr/bin/env python3
"""
Test script to verify the Firefox proxy endpoint is working.
"""

import requests
import sys
import time
from jupyterlab_firefox_launcher.server_proxy import launch_firefox, create_xpra_command

def test_configuration():
    """Test that our configuration is working correctly."""
    print("=== Testing Configuration ===")
    
    try:
        # Test launch_firefox function
        config = launch_firefox()
        print(f"✅ launch_firefox() returned config with {len(config)} keys")
        
        # Test command function
        command_func = config['command']
        if not callable(command_func):
            print("❌ Command is not callable!")
            return False
            
        # Test calling with port
        test_port = 9876
        command_list = command_func(port=test_port)
        print(f"✅ Command function generated {len(command_list)} arguments")
        
        # Check port substitution
        bind_arg = next((arg for arg in command_list if '--bind-tcp=' in arg), None)
        if not bind_arg or str(test_port) not in bind_arg:
            print(f"❌ Port substitution failed: {bind_arg}")
            return False
            
        print(f"✅ Port substitution working: {bind_arg}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_entry_point():
    """Test that the entry point is discoverable."""
    print("\n=== Testing Entry Point ===")
    
    try:
        import pkg_resources
        entry_points = list(pkg_resources.iter_entry_points('jupyter_server_proxy'))
        
        firefox_ep = None
        for ep in entry_points:
            if ep.name == 'firefox-desktop':
                firefox_ep = ep
                break
                
        if not firefox_ep:
            print("❌ firefox-desktop entry point not found!")
            print(f"Available entry points: {[ep.name for ep in entry_points]}")
            return False
            
        print(f"✅ Entry point found: {firefox_ep}")
        
        # Try loading the entry point
        loaded_func = firefox_ep.load()
        print(f"✅ Entry point loaded: {loaded_func}")
        
        # Test calling it
        config = loaded_func()
        print(f"✅ Entry point function returned config with keys: {list(config.keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Entry point test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint():
    """Test the actual HTTP endpoint."""
    print("\n=== Testing HTTP Endpoint ===")
    
    # Try different possible base URLs
    base_urls = [
        "http://localhost:8888",
        "http://127.0.0.1:8888",
        "http://0.0.0.0:8888",
    ]
    
    for base_url in base_urls:
        endpoint_url = f"{base_url}/proxy/firefox-desktop"
        
        try:
            print(f"Testing: {endpoint_url}")
            response = requests.get(endpoint_url, timeout=5, allow_redirects=False)
            
            print(f"Response: {response.status_code}")
            if response.status_code == 404:
                print(f"❌ 404 - Endpoint not found at {endpoint_url}")
                continue
            elif response.status_code == 200:
                print(f"✅ 200 - Endpoint working at {endpoint_url}")
                return True
            elif response.status_code in [302, 301]:
                print(f"🔄 {response.status_code} - Redirect to: {response.headers.get('Location', 'Unknown')}")
                return True
            else:
                print(f"⚠️  Unexpected status {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                
        except requests.ConnectionError:
            print(f"❌ Connection failed to {endpoint_url}")
        except requests.Timeout:
            print(f"⏰ Timeout connecting to {endpoint_url}")
        except Exception as e:
            print(f"❌ Error testing {endpoint_url}: {e}")
    
    return False

def check_server_running():
    """Check if JupyterLab server is running."""
    print("\n=== Checking JupyterLab Server ===")
    
    try:
        response = requests.get("http://localhost:8888/api/status", timeout=2)
        print(f"✅ JupyterLab server is running (status: {response.status_code})")
        
        # Try to get server info
        info_response = requests.get("http://localhost:8888/api/sessions", timeout=2)
        print(f"✅ API accessible (sessions: {info_response.status_code})")
        return True
        
    except requests.ConnectionError:
        print("❌ JupyterLab server not accessible at localhost:8888")
        print("💡 You may need to start JupyterLab: uv run jupyter lab --ip=0.0.0.0 --no-browser")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Firefox Launcher Proxy Endpoint\n")
    
    # Run tests in order
    config_ok = test_configuration()
    entry_ok = test_entry_point()
    server_ok = check_server_running()
    endpoint_ok = test_endpoint() if server_ok else False
    
    print("\n=== Test Summary ===")
    print(f"Configuration: {'✅' if config_ok else '❌'}")
    print(f"Entry Point:   {'✅' if entry_ok else '❌'}")
    print(f"Server:        {'✅' if server_ok else '❌'}")
    print(f"Endpoint:      {'✅' if endpoint_ok else '❌'}")
    
    if not server_ok:
        print("\n💡 Next steps:")
        print("1. Start JupyterLab: cd /home/bdx/allcode/github/vantagecompute/jupyterlab-firefox-launcher")
        print("2. Run: uv run jupyter lab --ip=0.0.0.0 --no-browser --allow-root")
        print("3. Re-run this test script")
        
    elif server_ok and not endpoint_ok:
        print("\n💡 The server is running but endpoint is 404.")
        print("This suggests jupyter-server-proxy needs to be restarted.")
        print("Try restarting JupyterLab to pick up the module changes.")
        
    elif endpoint_ok:
        print("\n🎉 All tests passed! The Firefox launcher should work.")
        
    return config_ok and entry_ok and server_ok and endpoint_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
