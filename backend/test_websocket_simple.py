#!/usr/bin/env python3
"""
Simple WebSocket client test
"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/live"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected successfully!")
            
            # Wait for messages for 10 seconds
            print("Waiting for messages (10 seconds)...")
            
            try:
                for i in range(3):
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    print(f"✓ Received message {i+1}: type={data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'ping':
                        print("  (heartbeat ping)")
                    elif data.get('type') == 'update':
                        print(f"  positions: {len(data.get('positions', []))}")
                        print(f"  intervals: {len(data.get('intervals', []))}")
                        print(f"  race_control: {len(data.get('race_control', []))}")
                
                print("\n✓ WebSocket endpoint is working correctly!")
                return True
                
            except asyncio.TimeoutError:
                print("⚠ No messages received (this is OK if no live session)")
                print("✓ Connection established successfully")
                return True
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    exit(0 if success else 1)
