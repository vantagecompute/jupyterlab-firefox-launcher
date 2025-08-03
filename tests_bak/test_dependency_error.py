#!/usr/bin/env python3
"""
Test script to demonstrate the custom HTML error page for missing dependencies.
"""

import tempfile
import os
from pathlib import Path
from jupyterlab_firefox_launcher.firefox_handler import _render_dependency_error_html

# Create mock missing dependencies
mock_missing_deps = [
    {
        "name": "Firefox",
        "description": "Web browser application required for browsing",
        "install_commands": [
            "# Ubuntu/Debian:",
            "sudo apt update && sudo apt install -y firefox",
            "",
            "# RHEL/CentOS/Fedora:",
            "sudo yum install -y firefox",
            "# or: sudo dnf install -y firefox",
            "",
            "# Manual download:",
            "# Visit https://www.mozilla.org/firefox/"
        ]
    },
    {
        "name": "Xpra",
        "description": "Remote display server required for launching Firefox in isolated sessions",
        "install_commands": [
            "# Ubuntu/Debian:",
            "sudo apt update && sudo apt install -y xpra",
            "",
            "# RHEL/CentOS/Fedora:",
            "sudo yum install -y xpra",
            "# or: sudo dnf install -y xpra",
            "",
            "# Conda:",
            "conda install -c conda-forge xpra"
        ]
    },
    {
        "name": "Xvfb",
        "description": "Virtual framebuffer for headless display",
        "install_commands": [
            "# Ubuntu/Debian:",
            "sudo apt update && sudo apt install -y xvfb",
            "",
            "# RHEL/CentOS/Fedora:",
            "sudo yum install -y xorg-x11-server-Xvfb",
            "# or: sudo dnf install -y xorg-x11-server-Xvfb"
        ]
    }
]

def main():
    print("🧪 Testing custom HTML error page rendering...")
    
    try:
        # Generate the HTML error page
        html_content = _render_dependency_error_html(mock_missing_deps)
        
        # Save to a temporary file and display info
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_path = f.name
        
        print(f"✅ Successfully rendered HTML error page")
        print(f"📄 HTML file size: {len(html_content):,} characters")
        print(f"💾 Temporary file saved to: {temp_path}")
        print(f"🌐 You can open it in a browser: file://{temp_path}")
        
        # Show a preview of the HTML
        print("\n📋 HTML Preview (first 500 characters):")
        print("-" * 60)
        print(html_content[:500] + "...")
        print("-" * 60)
        
        # Keep the file for inspection
        print(f"\n💡 The HTML file will remain at: {temp_path}")
        print("   You can open it in a browser to see the full error page.")
        
    except Exception as e:
        print(f"❌ Error testing HTML rendering: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
