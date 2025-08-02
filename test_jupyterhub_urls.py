#!/usr/bin/env python3
"""
Test script to verify JupyterHub URL routing for Firefox launcher extension.
"""

import json
import requests
import sys
from urllib.parse import urljoin

def test_firefox_launcher_endpoint(base_url, hub_prefix="/hub/user/test/"):
    """Test if the Firefox launcher endpoint is accessible."""
    
    # Construct the expected URL pattern
    if hub_prefix:
        api_url = urljoin(base_url, hub_prefix + "firefox-launcher/api/firefox")
    else:
        api_url = urljoin(base_url, "firefox-launcher/api/firefox")
    
    print(f"🔍 Testing Firefox launcher endpoint: {api_url}")
    
    try:
        # Test with status check parameter
        test_url = f"{api_url}?status=check"
        print(f"   GET {test_url}")
        
        response = requests.get(test_url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
                return True
            except json.JSONDecodeError:
                print(f"   Response (text): {response.text}")
                return True
        elif response.status_code == 404:
            print(f"   ❌ 404 Not Found - endpoint not registered correctly")
            return False
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing JupyterHub URL routing for Firefox launcher...")
    
    # Determine base URL from command line or default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Default to the URL pattern shown in the error
        base_url = "http://raton00:8888"
    
    print(f"📍 Base URL: {base_url}")
    
    # Test scenarios
    test_cases = [
        ("Direct (no hub prefix)", ""),
        ("JupyterHub user path", "/hub/user/test/"),
        ("JupyterHub alternative", "/hub/firefox-launcher/"),
    ]
    
    for description, hub_prefix in test_cases:
        print(f"\n🔸 {description}")
        success = test_firefox_launcher_endpoint(base_url, hub_prefix)
        if success:
            print(f"   ✅ SUCCESS")
        else:
            print(f"   ❌ FAILED")
    
    print(f"\n🏁 Test completed")

if __name__ == "__main__":
    main()
