#!/usr/bin/env python3
"""
Test script to verify that all Xpra static files are being served correctly
by the JupyterLab Firefox launcher extension.
"""

import requests
import json

# JupyterLab is running on port 8890
BASE_URL = "http://localhost:8890/firefox-launcher"

# Critical Xpra HTML5 client files that must be available
REQUIRED_FILES = [
    "js/lib/jquery.js",
    "js/lib/rencode.js", 
    "js/lib/jquery-ui.js",
    "js/lib/lz4.js",
    "js/Client.js",
    "css/client.css",
    "css/connect.css"
]

def test_static_files():
    """Test that all required static files are accessible."""
    results = {"success": [], "failed": []}
    
    for file_path in REQUIRED_FILES:
        url = f"{BASE_URL}/{file_path}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results["success"].append({
                    "file": file_path,
                    "status": response.status_code,
                    "content_type": response.headers.get("content-type", "unknown"),
                    "size": len(response.content)
                })
            else:
                results["failed"].append({
                    "file": file_path, 
                    "status": response.status_code,
                    "error": f"HTTP {response.status_code}"
                })
        except Exception as e:
            results["failed"].append({
                "file": file_path,
                "status": "error", 
                "error": str(e)
            })
    
    return results

def main():
    print("🧪 Testing JupyterLab Firefox Launcher Static File Handler")
    print("=" * 60)
    
    results = test_static_files()
    
    print(f"\n✅ Successfully served files: {len(results['success'])}")
    for file_info in results['success']:
        print(f"   📄 {file_info['file']} ({file_info['content_type']}, {file_info['size']} bytes)")
    
    if results['failed']:
        print(f"\n❌ Failed files: {len(results['failed'])}")
        for file_info in results['failed']:
            print(f"   📄 {file_info['file']} - {file_info['error']}")
    
    # Test result summary
    total_files = len(REQUIRED_FILES)
    success_count = len(results['success'])
    
    print(f"\n📊 Summary: {success_count}/{total_files} files successfully served")
    
    if success_count == total_files:
        print("🎉 All static files are working! The compression and static file fixes are complete.")
        return True
    else:
        print("⚠️  Some files are still missing. Check the XpraStaticHandler implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
