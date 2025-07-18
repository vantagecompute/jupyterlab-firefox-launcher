#!/usr/bin/env python3
"""
Version Sync Script - Keep package.json in sync with pyproject.toml version
"""

import json
import os
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Python < 3.11
    except ImportError:
        print("❌ Error: tomli package required for Python < 3.11")
        print("Install with: pip install tomli")
        sys.exit(1)

def get_pyproject_version():
    """Get version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")
    
    with open(pyproject_path, 'rb') as f:
        data = tomllib.load(f)
    
    version = data.get('project', {}).get('version')
    if not version:
        raise ValueError("Version not found in pyproject.toml [project] section")
    
    return version

def update_package_json_version(version):
    """Update frontend package.json version"""
    package_json_path = Path("jupyterlab_firefox_launcher/labextension/package.json")

    files_updated = []
    
    for path in [package_json_path]:
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
        # Get version from pyproject.toml
        pyproject_version = get_pyproject_version()
        print(f"📦 pyproject.toml version: {pyproject_version}")
        
        # Update package.json files
        updated_files = update_package_json_version(pyproject_version)
        
        if updated_files:
            print("\n✅ Updated versions:")
            for update in updated_files:
                print(f"   {update}")
        else:
            print("\n⚠️  No package.json files found to update")
        
        print(f"\n🎯 All versions now synchronized to: {pyproject_version}")
        
    except Exception as e:
        print(f"❌ Error syncing versions: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
