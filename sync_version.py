#!/usr/bin/env python3
"""
Version Sync Script - Keep package.json and pyproject.toml versions in sync
"""

import json
import os
import sys
from pathlib import Path

def get_python_version():
    """Get version from Python package __init__.py"""
    sys.path.insert(0, 'jupyterlab_firefox_launcher')
    from jupyterlab_firefox_launcher import __version__
    return __version__

def update_package_json_version(version):
    """Update frontend package.json version"""
    package_json_path = Path("package.json")
    labextension_package_json_path = Path("jupyterlab_firefox_launcher/labextension/package.json")
    
    files_updated = []
    
    for path in [package_json_path, labextension_package_json_path]:
        if path.exists():
            with open(path, 'r') as f:
                package_data = json.load(f)
            
            old_version = package_data.get('version', 'unknown')
            package_data['version'] = version
            
            with open(path, 'w') as f:
                json.dump(package_data, f, indent=2)
                f.write('\n')  # Add trailing newline
            
            files_updated.append(f"{path}: {old_version} → {version}")
    
    return files_updated

def main():
    print("🔄 Version Sync Script")
    print("=" * 30)
    
    try:
        # Get version from Python package
        python_version = get_python_version()
        print(f"📦 Python package version: {python_version}")
        
        # Update package.json files
        updated_files = update_package_json_version(python_version)
        
        if updated_files:
            print("\n✅ Updated versions:")
            for update in updated_files:
                print(f"   {update}")
        else:
            print("\n⚠️  No package.json files found to update")
        
        print(f"\n🎯 All versions now synchronized to: {python_version}")
        
    except Exception as e:
        print(f"❌ Error syncing versions: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
