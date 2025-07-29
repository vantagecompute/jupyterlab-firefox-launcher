#!/usr/bin/env python3
"""
Copyright (c) 2025 Vantage Compute Corporation.

Update documentation version from pyproject.toml
This script reads the version from pyproject.toml and updates the Jekyll data file.
"""

import toml
import datetime
import os
from pathlib import Path

def update_docs_version():
    """Update the documentation version from pyproject.toml"""
    
    # Get the root directory (where pyproject.toml is located)
    root_dir = Path(__file__).parent.parent
    pyproject_path = root_dir / "pyproject.toml"
    docs_data_path = root_dir / "docs" / "_data" / "project.yml"
    
    # Read version from pyproject.toml
    try:
        with open(pyproject_path, 'r') as f:
            data = toml.load(f)
        
        version = data['project']['version']
        updated = datetime.datetime.now().strftime('%Y-%m-%d')
        
        print(f"Found version: {version}")
        
        # Create the docs/_data directory if it doesn't exist
        docs_data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the updated data file
        with open(docs_data_path, 'w') as f:
            f.write(f"""# Copyright (c) 2025 Vantage Compute Corporation.
# Project metadata - auto-generated, do not edit manually
version: "{version}"
updated: "{updated}"
""")
        
        print(f"Updated {docs_data_path} with version {version}")
        return True
        
    except Exception as e:
        print(f"Error updating documentation version: {e}")
        return False

if __name__ == "__main__":
    success = update_docs_version()
    exit(0 if success else 1)
