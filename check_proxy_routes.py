#!/usr/bin/env python3
"""
Quick script to check JupyterHub proxy routes using the auth token.
"""
import requests
import json

# Use the auth token from the config
AUTH_TOKEN = 'a1d186378e6cb9ac36342769de67fc0e7eb3d9ff2e9e5a89f93976a272658dfa'
API_URL = 'http://127.0.0.1:8001'

def check_proxy_routes():
    """Check the current proxy routes."""
    try:
        response = requests.get(
            f"{API_URL}/api/routes",
            headers={"Authorization": f"token {AUTH_TOKEN}"},
            timeout=5
        )
        
        if response.status_code == 200:
            routes = response.json()
            print("✅ Successfully retrieved proxy routes:")
            print(json.dumps(routes, indent=2))
            
            # Look for Firefox proxy routes
            firefox_routes = {k: v for k, v in routes.items() if 'proxy' in k}
            if firefox_routes:
                print(f"\n🦊 Found {len(firefox_routes)} proxy routes:")
                for route, target in firefox_routes.items():
                    print(f"  {route} -> {target}")
            else:
                print("\n❌ No proxy routes found")
                
        else:
            print(f"❌ Failed to get routes: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking routes: {e}")

if __name__ == "__main__":
    check_proxy_routes()
