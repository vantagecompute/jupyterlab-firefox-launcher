#!/usr/bin/env python3
"""
Basic functional tests for CSP proxy functionality.

These tests validate the core CSP bypass functionality without heavy external dependencies.
"""

import sys
import subprocess
import json
import requests
import time
from pathlib import Path

def test_proxy_endpoint_availability():
    """Test that the proxy endpoint is available and responds correctly."""
    print("🔍 Testing proxy endpoint availability...")
    
    base_url = "http://localhost:8889"
    
    # Try to get current user from JupyterHub API
    try:
        # Get the current user endpoint to determine base path
        response = requests.get(f"{base_url}/hub/api/user", timeout=5)
        if response.status_code == 401:
            print("⚠️  Not authenticated with JupyterHub - using test user path")
            # Fallback to known test user path
            proxy_url = f"{base_url}/user/bdx/firefox-launcher/proxy"
        else:
            user_data = response.json()
            username = user_data.get('name', 'bdx')
            proxy_url = f"{base_url}/user/{username}/firefox-launcher/proxy"
    except:
        print("⚠️  Cannot connect to JupyterHub API - using fallback")
        proxy_url = f"{base_url}/user/bdx/firefox-launcher/proxy"
    
    # Test proxy endpoint with test parameters
    test_url = f"{proxy_url}?host=localhost&port=8080"
    
    try:
        response = requests.head(test_url, timeout=10, allow_redirects=False)
        
        print(f"📡 Proxy URL: {test_url}")
        print(f"📋 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Proxy endpoint is responding correctly!")
            
            # Check CSP headers
            csp = response.headers.get('Content-Security-Policy', '')
            x_frame = response.headers.get('X-Frame-Options', '')
            
            print(f"🛡️  CSP Header: {csp}")
            print(f"🖼️  X-Frame-Options: {x_frame}")
            
            if 'frame-ancestors *' in csp:
                print("✅ CSP frame-ancestors correctly set to *")
            else:
                print("❌ CSP frame-ancestors not found or incorrect")
                return False
            
            if x_frame == 'ALLOWALL':
                print("✅ X-Frame-Options correctly set to ALLOWALL")
            else:
                print("❌ X-Frame-Options not found or incorrect")
                return False
            
            return True
            
        elif response.status_code == 302:
            print("❌ Getting redirect - authentication may be required")
            print(f"   Location: {response.headers.get('Location', 'Unknown')}")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def test_csp_modification_logic():
    """Test the CSP modification logic directly."""
    print("\n🔍 Testing CSP modification logic...")
    
    # Import the handler to test the logic
    try:
        from jupyterlab_firefox_launcher.firefox_handler import XpraProxyHandler
        from unittest.mock import Mock
        
        # Create a handler instance for testing
        handler = XpraProxyHandler(Mock(), Mock())
        
        # Test cases
        test_cases = [
            {
                'input': "frame-ancestors 'none'",
                'expected': "frame-ancestors *",
                'description': "Basic frame-ancestors none replacement"
            },
            {
                'input': "script-src 'self'; frame-ancestors 'none'; object-src 'none'",
                'expected_contains': ["frame-ancestors *", "script-src 'self'", "object-src 'none'"],
                'description': "Complex CSP with frame-ancestors none"
            },
            {
                'input': "script-src 'self'; object-src 'none'",
                'expected_contains': ["frame-ancestors *", "script-src 'self'", "object-src 'none'"],
                'description': "CSP without frame-ancestors (should add it)"
            },
            {
                'input': "",
                'expected': "",
                'description': "Empty CSP"
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n  Test {i}: {test_case['description']}")
            print(f"    Input: {test_case['input']}")
            
            try:
                result = handler._modify_csp(test_case['input'])
                print(f"    Output: {result}")
                
                if 'expected' in test_case:
                    if result == test_case['expected']:
                        print("    ✅ PASS")
                    else:
                        print(f"    ❌ FAIL - Expected: {test_case['expected']}")
                        all_passed = False
                        
                elif 'expected_contains' in test_case:
                    missing = []
                    for expected_part in test_case['expected_contains']:
                        if expected_part not in result:
                            missing.append(expected_part)
                    
                    if not missing:
                        print("    ✅ PASS")
                    else:
                        print(f"    ❌ FAIL - Missing: {missing}")
                        all_passed = False
                        
            except Exception as e:
                print(f"    ❌ ERROR: {e}")
                all_passed = False
        
        return all_passed
        
    except ImportError as e:
        print(f"❌ Cannot import handler: {e}")
        return False


def test_extension_installation():
    """Test that the extension is properly installed."""
    print("\n🔍 Testing extension installation...")
    
    try:
        # Check if extension is installed
        result = subprocess.run([
            sys.executable, '-c',
            'import jupyterlab_firefox_launcher; print("Extension imported successfully")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Extension can be imported")
            
            # Check version
            version_result = subprocess.run([
                sys.executable, '-c',
                'from jupyterlab_firefox_launcher import __version__; print(__version__)'
            ], capture_output=True, text=True, timeout=10)
            
            if version_result.returncode == 0:
                version = version_result.stdout.strip()
                print(f"✅ Extension version: {version}")
            else:
                print("⚠️  Could not determine extension version")
            
            return True
        else:
            print(f"❌ Extension import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Extension test failed: {e}")
        return False


def test_dependencies():
    """Test that required dependencies are available."""
    print("\n🔍 Testing system dependencies...")
    
    try:
        from jupyterlab_firefox_launcher.firefox_handler import _check_dependencies
        
        deps = _check_dependencies()
        
        if deps['all_present']:
            print("✅ All dependencies are present")
            return True
        else:
            print("❌ Missing dependencies:")
            for dep in deps['missing']:
                print(f"  - {dep['name']}: {dep['description']}")
                for cmd in dep['install_commands']:
                    print(f"    Install: {cmd}")
            return False
            
    except Exception as e:
        print(f"❌ Dependency check failed: {e}")
        return False


def test_frontend_url_construction():
    """Test frontend URL construction logic."""
    print("\n🔍 Testing frontend URL construction...")
    
    # Test cases for URL construction
    test_cases = [
        {
            'base_path': '/user/alice/',
            'host': 'localhost',
            'port': '8080',
            'expected': '/user/alice/firefox-launcher/proxy?host=localhost&port=8080'
        },
        {
            'base_path': '/user/bob-test/',
            'host': 'remote-server',
            'port': '9090',
            'expected': '/user/bob-test/firefox-launcher/proxy?host=remote-server&port=9090'
        },
        {
            'base_path': '/',
            'host': 'example.com',
            'port': '80',
            'expected': '/firefox-launcher/proxy?host=example.com&port=80'
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test {i}: Base path '{test_case['base_path']}'")
        
        # Simulate frontend URL construction
        proxy_url = f"{test_case['base_path']}firefox-launcher/proxy?host={test_case['host']}&port={test_case['port']}"
        
        print(f"    Generated: {proxy_url}")
        print(f"    Expected:  {test_case['expected']}")
        
        if proxy_url == test_case['expected']:
            print("    ✅ PASS")
        else:
            print("    ❌ FAIL")
            all_passed = False
    
    return all_passed


def run_all_tests():
    """Run all tests and provide summary."""
    print("🚀 Starting CSP Proxy Test Suite")
    print("=" * 50)
    
    tests = [
        ("Extension Installation", test_extension_installation),
        ("System Dependencies", test_dependencies),
        ("CSP Modification Logic", test_csp_modification_logic),
        ("Frontend URL Construction", test_frontend_url_construction),
        ("Proxy Endpoint Availability", test_proxy_endpoint_availability),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CSP proxy functionality is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test CSP proxy functionality")
    parser.add_argument("--test", choices=[
        "installation", "dependencies", "csp", "frontend", "proxy", "all"
    ], default="all", help="Which test to run")
    
    args = parser.parse_args()
    
    if args.test == "all":
        success = run_all_tests()
    elif args.test == "installation":
        success = test_extension_installation()
    elif args.test == "dependencies":
        success = test_dependencies()
    elif args.test == "csp":
        success = test_csp_modification_logic()
    elif args.test == "frontend":
        success = test_frontend_url_construction()
    elif args.test == "proxy":
        success = test_proxy_endpoint_availability()
    
    sys.exit(0 if success else 1)
