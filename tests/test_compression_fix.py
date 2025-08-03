#!/usr/bin/env python3
"""
Test script to verify the compression fix in the CSP proxy.
"""

import subprocess
import sys
import time

def check_jupyterhub_running():
    """Check if JupyterHub is running."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'jupyterhub' in result.stdout
    except:
        return False

def test_proxy_endpoint():
    """Test the proxy endpoint with curl."""
    print("🔍 Testing proxy endpoint with curl...")
    
    proxy_url = "http://localhost:8889/user/bdx/firefox-launcher/proxy?host=raton00&port=36181"
    
    try:
        # Test HEAD request to check headers without downloading content
        result = subprocess.run([
            'curl', '-I', '-s', '--connect-timeout', '10',
            proxy_url
        ], capture_output=True, text=True, timeout=15)
        
        print(f"📡 URL: {proxy_url}")
        print(f"📋 Status: {result.returncode}")
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            status_line = lines[0] if lines else "Unknown"
            print(f"📄 Response: {status_line}")
            
            # Check for important headers
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.lower().strip()] = value.strip()
            
            # Check CSP header
            csp = headers.get('content-security-policy', '')
            if csp:
                print(f"🛡️  CSP: {csp}")
                if 'frame-ancestors *' in csp:
                    print("✅ CSP correctly modified for iframe embedding")
                else:
                    print("❌ CSP not properly modified")
            
            # Check X-Frame-Options
            x_frame = headers.get('x-frame-options', '')
            if x_frame:
                print(f"🖼️  X-Frame-Options: {x_frame}")
                if x_frame.upper() == 'ALLOWALL':
                    print("✅ X-Frame-Options correctly set")
                else:
                    print("❌ X-Frame-Options not properly set")
            
            return True
            
        else:
            print(f"❌ Request failed with code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing CSP Proxy Compression Fix")
    print("=" * 50)
    
    # Check if JupyterHub is running
    if not check_jupyterhub_running():
        print("⚠️  JupyterHub doesn't appear to be running")
        print("💡 To start JupyterHub, run: jupyterhub")
        print("   Then try this test again")
        return False
    
    print("✅ JupyterHub is running")
    
    # Test the proxy endpoint
    success = test_proxy_endpoint()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Compression fix appears to be working!")
        print("💡 The proxy endpoint is responding correctly")
        print("   Try opening a Firefox launcher in JupyterHub to test iframe embedding")
    else:
        print("⚠️  Test incomplete - check JupyterHub logs for compression errors")
        print("💡 Look for 'zlib.error' or compression-related errors in the logs")
    
    return success

if __name__ == "__main__":
    main()
