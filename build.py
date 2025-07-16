#!/usr/bin/env python3
"""
Build script that syncs versions before building
"""

import subprocess
import sys
import os

def main():
    print("🚀 Starting Firefox Launcher Build Process")
    print("=" * 50)
    
    # Step 1: Sync versions
    print("🔄 Step 1: Syncing versions...")
    try:
        result = subprocess.run(["python3", "sync_version.py"], check=True)
        print("✅ Version sync completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Version sync failed: {e}")
        return 1
    
    # Step 2: Build with uv
    print("\n🔨 Step 2: Building package...")
    try:
        result = subprocess.run(["uv", "build"], check=True)
        print("✅ Package build completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Package build failed: {e}")
        return 1
    
    print("\n🎉 Build process completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
