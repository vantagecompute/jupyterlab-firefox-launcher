#!/usr/bin/env python3
"""
Debug script to check what jupyter-server-proxy sees and creates
"""

import sys
import os
sys.path.insert(0, 'jupyterlab_firefox_launcher')

from jupyterlab_firefox_launcher.server_proxy import setup_firefox_desktop

print("🔍 Debugging Server Proxy Configuration")
print("=" * 50)

# Get the configuration
try:
    config = setup_firefox_desktop()
    
    print("📋 Current Server Proxy Configuration:")
    for key, value in config.items():
        if key == 'command':
            print(f"   {key}: {' '.join(value[:3])}... (truncated)")
        elif callable(value):
            print(f"   {key}: <function>")
        else:
            print(f"   {key}: {value}")
    
    print("\n🎯 Key Findings:")
    
    # Check for launcher_entry
    if 'launcher_entry' in config:
        launcher = config['launcher_entry']
        print(f"❌ SERVER PROXY LAUNCHER FOUND:")
        print(f"   Title: {launcher.get('title', 'N/A')}")
        print(f"   Path: {launcher.get('path_info', 'N/A')}")
        print("   This creates the launcher in Notebooks section!")
    else:
        print("✅ No server proxy launcher_entry found")
    
    # Check new_browser_window setting
    new_window = config.get('new_browser_window', True)
    print(f"📄 new_browser_window: {new_window}")
    
    # Check if we can disable server proxy launcher
    if 'launcher_entry' not in config:
        print("\n💡 Server proxy should NOT create launcher")
        print("   Only frontend extension should create launcher")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📝 Expected Behavior:")
print("   ✅ Only ONE launcher icon in 'Other' category (from frontend)")
print("   ❌ NO launcher icon in 'Notebooks' category (from server proxy)")
