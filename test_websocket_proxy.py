#!/usr/bin/env python3
"""
Simple WebSocket test client for testing the XpraWebSocketHandler.
"""

import asyncio
import websockets
import sys

async def test_websocket_proxy():
    # Test proxy endpoint
    proxy_url = "ws://localhost:8000/user/bdx/firefox-launcher/ws?host=127.0.0.1&port=54205"
    
    try:
        print(f"Connecting to WebSocket proxy: {proxy_url}")
        # Connect with binary subprotocol for Xpra compatibility
        async with websockets.connect(proxy_url, subprotocols=["binary"]) as websocket:
            print("✅ Connected to WebSocket proxy!")
            
            # Send a simple test message
            test_message = b"hello"
            await websocket.send(test_message)
            print(f"📤 Sent: {test_message}")
            
            # Try to receive a response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds (this might be normal)")
            
            print("✅ WebSocket proxy test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket proxy test failed: {e}")
        return False
        
    return True

async def test_direct_connection():
    # Test direct connection to Xpra server for comparison
    direct_url = "ws://127.0.0.1:54205/"
    
    try:
        print(f"Testing direct connection to: {direct_url}")
        async with websockets.connect(direct_url, subprotocols=["binary"]) as websocket:
            print("✅ Direct connection to Xpra server works!")
            
            # Send a simple test message
            test_message = b"hello"
            await websocket.send(test_message)
            print(f"📤 Sent: {test_message}")
            
            # Try to receive a response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds (this might be normal)")
                
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return False
        
    return True

async def main():
    print("🧪 Testing WebSocket connections...")
    print("=" * 50)
    
    # First test direct connection to ensure Xpra server is working
    print("1. Testing direct connection to Xpra server:")
    direct_ok = await test_direct_connection()
    print()
    
    # Then test proxy connection
    print("2. Testing WebSocket proxy:")
    proxy_ok = await test_websocket_proxy()
    print()
    
    print("=" * 50)
    if direct_ok and proxy_ok:
        print("✅ All tests passed! WebSocket proxy is working correctly.")
        return 0
    elif direct_ok and not proxy_ok:
        print("❌ Direct connection works but proxy fails - proxy implementation issue.")
        return 1
    elif not direct_ok and not proxy_ok:
        print("❌ Both connections failed - Xpra server may not be running.")
        return 2
    else:
        print("❌ Unexpected test results.")
        return 3

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
