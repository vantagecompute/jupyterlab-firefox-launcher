#!/usr/bin/env python3
"""
Custom Hatch Build Hook - Sync versions before build
"""

import subprocess
import sys
from pathlib import Path

from hatchling.plugin import hookimpl

@hookimpl
def hatch_build_hook(root: str, build_data: dict) -> None:
    """Run version sync before build"""
    print("🔄 Running version sync before build...")
    
    # Change to project root
    project_root = Path(root)
    sync_script = project_root / "sync_version.py"
    
    if sync_script.exists():
        try:
            result = subprocess.run([
                sys.executable, str(sync_script)
            ], cwd=project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Version sync completed successfully")
                print(result.stdout)
            else:
                print(f"⚠️  Version sync warning: {result.stderr}")
                print(result.stdout)
        except Exception as e:
            print(f"⚠️  Could not run version sync: {e}")
    else:
        print("⚠️  sync_version.py not found, skipping version sync")
