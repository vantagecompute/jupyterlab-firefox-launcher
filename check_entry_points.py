#!/usr/bin/env python3
"""
Check entry points to debug registration issues.
"""

import sys
import subprocess

def check_entry_points():
    """Check entry points using multiple methods."""
    print("=== Entry Point Debugging ===\n")
    
    # Method 1: Using importlib_metadata (modern approach)
    try:
        from importlib.metadata import entry_points
        print("✅ Using importlib.metadata")
        
        # Get all entry points
        all_eps = entry_points()
        
        # Check jupyter_serverproxy_servers specifically
        proxy_eps = all_eps.select(group='jupyter_serverproxy_servers')
        if proxy_eps:
            print(f"✅ jupyter_serverproxy_servers group found with {len(proxy_eps)} entries:")
            for ep in proxy_eps:
                print(f"  - {ep.name} = {ep.value}")
        else:
            print("❌ jupyter_serverproxy_servers group not found")
            
        # Check jupyter_server_extensions
        server_eps = all_eps.select(group='jupyter_server_extensions')
        if server_eps:
            print(f"✅ jupyter_server_extensions group found with {len(server_eps)} entries:")
            for ep in server_eps:
                print(f"  - {ep.name} = {ep.value}")
        else:
            print("❌ jupyter_server_extensions group not found")
            
        # Show all groups that exist
        groups = set()
        for ep in all_eps:
            groups.add(ep.group)
        print(f"All available groups: {sorted(groups)}")
            
    except ImportError as e:
        print(f"❌ importlib.metadata failed: {e}")
    except Exception as e:
        print(f"❌ importlib.metadata error: {e}")
    
    print()
    
    # Method 2: Using pkg_resources (deprecated but still works)
    try:
        import pkg_resources
        print("✅ Using pkg_resources (deprecated)")
        
        # Check jupyter_serverproxy_servers
        proxy_eps = list(pkg_resources.iter_entry_points('jupyter_serverproxy_servers'))
        if proxy_eps:
            print(f"✅ Found {len(proxy_eps)} jupyter_serverproxy_servers entries:")
            for ep in proxy_eps:
                print(f"  - {ep.name} = {ep.module_name}:{ep.attrs[0] if ep.attrs else 'NO_ATTRS'}")
        else:
            print("❌ No jupyter_serverproxy_servers entries found")
            
        # Check jupyter_server_extensions  
        server_eps = list(pkg_resources.iter_entry_points('jupyter_server_extensions'))
        if server_eps:
            print(f"✅ Found {len(server_eps)} jupyter_server_extensions entries:")
            for ep in server_eps:
                print(f"  - {ep.name} = {ep.module_name}:{ep.attrs[0] if ep.attrs else 'NO_ATTRS'}")
        else:
            print("❌ No jupyter_server_extensions entries found")
            
    except ImportError as e:
        print(f"❌ pkg_resources failed: {e}")
    
    print()
    
    # Method 3: Check pip show output
    try:
        result = subprocess.run(
            ['uv', 'pip', 'show', 'jupyterlab-firefox-launcher'], 
            capture_output=True, 
            text=True,
            check=True
        )
        print("✅ Package info from pip:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ pip show failed: {e}")
    except FileNotFoundError:
        print("❌ pip command not found")
    
    print()
    
    # Method 4: Check specific entry point loading
    try:
        from importlib.metadata import entry_points
        all_eps = entry_points()
        
        proxy_eps = all_eps.select(group='jupyter_serverproxy_servers')
        for ep in proxy_eps:
            if ep.name == 'firefox-desktop':
                print(f"✅ Found firefox-desktop entry point: {ep.value}")
                try:
                    loaded_func = ep.load()
                    print(f"✅ Successfully loaded function: {loaded_func}")
                    
                    # Test the function
                    config = loaded_func()
                    print(f"✅ Function returns config with keys: {list(config.keys())}")
                    
                except Exception as e:
                    print(f"❌ Failed to load/test function: {e}")
                break
        else:
            print("❌ firefox-desktop entry point not found in jupyter_serverproxy_servers")
            
    except Exception as e:
        print(f"❌ Entry point testing failed: {e}")

if __name__ == "__main__":
    check_entry_points()
