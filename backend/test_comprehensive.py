#!/usr/bin/env python3
"""
Comprehensive backend verification script
Tests all REST endpoints, WebSocket, Redis caching, and request ID propagation
"""

import httpx
import asyncio
import websockets
import json
import subprocess
import time
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

class BackendVerifier:
    def __init__(self):
        self.rest_results: List[Tuple[str, bool, str]] = []
        self.ws_results: List[Tuple[str, bool, str]] = []
        self.cache_results: List[Tuple[str, bool, str]] = []
        self.request_id_results: List[Tuple[str, bool, str]] = []
        
    async def test_rest_endpoint(self, method: str, path: str, description: str):
        """Test a single REST endpoint"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{path}")
                elif method == "POST":
                    response = await client.post(f"{BASE_URL}{path}", json={})
                
                if response.status_code in [200, 201]:
                    self.rest_results.append((description, True, f"Status {response.status_code}"))
                    return True, response
                else:
                    self.rest_results.append((description, False, 
                                            f"Status {response.status_code}: {response.text[:100]}"))
                    return False, response
                    
        except Exception as e:
            self.rest_results.append((description, False, str(e)[:100]))
            return False, None
    
    async def test_websocket(self, path: str, description: str):
        """Test WebSocket endpoint"""
        try:
            async with websockets.connect(f"{WS_URL}{path}", timeout=10) as ws:
                # Wait for initial message or ping
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    data = json.loads(message)
                    self.ws_results.append((description, True, f"Connected, received: {data.get('type', 'data')}"))
                    return True
                except asyncio.TimeoutError:
                    # No message received but connection established
                    self.ws_results.append((description, True, "Connected successfully"))
                    return True
        except Exception as e:
            self.ws_results.append((description, False, str(e)[:100]))
            return False
    
    def test_redis_cache(self):
        """Test Redis caching by checking for cache keys"""
        try:
            result = subprocess.run(
                ["redis-cli", "KEYS", "cache:*"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                keys = result.stdout.strip().split('\n')
                key_count = len([k for k in keys if k])
                
                if key_count > 0:
                    self.cache_results.append(("Redis cache keys exist", True, f"Found {key_count} cached items"))
                    return True
                else:
                    self.cache_results.append(("Redis cache keys exist", False, "No cache keys found"))
                    return False
            else:
                self.cache_results.append(("Redis connection", False, "Could not connect to Redis"))
                return False
                
        except FileNotFoundError:
            self.cache_results.append(("Redis CLI", False, "redis-cli not found in PATH"))
            return False
        except Exception as e:
            self.cache_results.append(("Redis test", False, str(e)[:100]))
            return False
    
    async def test_request_id_propagation(self):
        """Test that request IDs are properly propagated"""
        try:
            custom_id = "test-request-12345"
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/health",
                    headers={"X-Request-ID": custom_id}
                )
                
                # Check if request ID is in response headers
                response_id = response.headers.get("X-Request-ID")
                
                if response_id == custom_id:
                    self.request_id_results.append(("Request ID propagation", True, 
                                                   f"ID correctly returned: {custom_id}"))
                    return True
                else:
                    self.request_id_results.append(("Request ID propagation", False, 
                                                   f"Expected {custom_id}, got {response_id}"))
                    return False
                    
        except Exception as e:
            self.request_id_results.append(("Request ID test", False, str(e)[:100]))
            return False
    
    def print_section(self, title: str, results: List[Tuple[str, bool, str]]):
        """Print a section of results"""
        print(f"\n{CYAN}{'='*80}{RESET}")
        print(f"{CYAN}{title}{RESET}")
        print(f"{CYAN}{'='*80}{RESET}\n")
        
        passed = sum(1 for _, p, _ in results if p)
        total = len(results)
        
        for description, success, message in results:
            status = f"{GREEN}✓{RESET}" if success else f"{RED}✗{RESET}"
            print(f"{status} {description}")
            if not success or "Error" in message:
                print(f"  {YELLOW}{message}{RESET}")
        
        print(f"\n{BLUE}Passed: {passed}/{total}{RESET}")
    
    def print_summary(self):
        """Print overall summary"""
        all_results = (self.rest_results + self.ws_results + 
                      self.cache_results + self.request_id_results)
        total_passed = sum(1 for _, p, _ in all_results if p)
        total = len(all_results)
        
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}OVERALL SUMMARY{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")
        print(f"\nTotal Tests: {total}")
        print(f"{GREEN}Passed: {total_passed}{RESET}")
        print(f"{RED}Failed: {total - total_passed}{RESET}")
        print(f"Success Rate: {(total_passed/total*100):.1f}%\n")
        
        return total_passed == total


async def main():
    verifier = BackendVerifier()
    
    print(f"{YELLOW}{'='*80}{RESET}")
    print(f"{YELLOW}F1 DASHBOARD BACKEND COMPREHENSIVE VERIFICATION{RESET}")
    print(f"{YELLOW}{'='*80}{RESET}\n")
    
    # Test REST endpoints
    print(f"{BLUE}Testing REST Endpoints (22 total)...{RESET}\n")
    
    # Health check
    await verifier.test_rest_endpoint("GET", "/health", "1. Health Check")
    
    # Standings (2)
    await verifier.test_rest_endpoint("GET", "/api/standings/drivers/2024", "2. Driver Standings")
    await verifier.test_rest_endpoint("GET", "/api/standings/constructors/2024", "3. Constructor Standings")
    
    # Races (4)
    await verifier.test_rest_endpoint("GET", "/api/races/2024", "4. Race Schedule")
    await verifier.test_rest_endpoint("GET", "/api/races/2024/1/results", "5. Race Results")
    await verifier.test_rest_endpoint("GET", "/api/races/2024/1/qualifying", "6. Qualifying Results")
    await verifier.test_rest_endpoint("GET", "/api/races/2024/1/laps", "7. Lap Times")
    
    # Analytics (7) - using correct driver ID format
    await verifier.test_rest_endpoint("GET", "/api/analytics/trends/max_verstappen/2024", "8. Performance Trends")
    await verifier.test_rest_endpoint("GET", "/api/analytics/consistency/max_verstappen/2024", "9. Consistency Score")
    await verifier.test_rest_endpoint("GET", "/api/analytics/form/max_verstappen/2024", "10. Form Indicator")
    await verifier.test_rest_endpoint("GET", "/api/analytics/dnf/max_verstappen/2024", "11. DNF Rate")
    
    # Driver comparison is POST with JSON body
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/analytics/compare",
                json={"driver_ids": ["max_verstappen", "hamilton"], "year": "2024"}
            )
            if response.status_code == 200:
                verifier.rest_results.append(("12. Driver Comparison", True, f"Status {response.status_code}"))
            else:
                verifier.rest_results.append(("12. Driver Comparison", False, 
                                            f"Status {response.status_code}: {response.text[:100]}"))
        except Exception as e:
            verifier.rest_results.append(("12. Driver Comparison", False, str(e)[:100]))
    
    await verifier.test_rest_endpoint("GET", "/api/analytics/circuit/monza?year=2024", "13. Circuit Performance")
    await verifier.test_rest_endpoint("GET", "/api/analytics/projection/2026", "14. Championship Projection")  # Use current year
    
    # Live data (8)
    await verifier.test_rest_endpoint("GET", "/api/live/session", "15. Current Session")
    await verifier.test_rest_endpoint("GET", "/api/live/drivers?session_key=latest", "16. Session Drivers")
    await verifier.test_rest_endpoint("GET", "/api/live/positions?session_key=latest", "17. Live Positions")
    await verifier.test_rest_endpoint("GET", "/api/live/intervals?session_key=latest", "18. Live Intervals")
    await verifier.test_rest_endpoint("GET", "/api/live/stints?session_key=latest", "19. Live Stints")
    await verifier.test_rest_endpoint("GET", "/api/live/pits?session_key=latest", "20. Live Pit Stops")
    await verifier.test_rest_endpoint("GET", "/api/live/weather?session_key=latest", "21. Live Weather")
    await verifier.test_rest_endpoint("GET", "/api/live/racecontrol?session_key=latest", "22. Race Control")
    
    verifier.print_section("REST ENDPOINTS", verifier.rest_results)
    
    # Test WebSocket endpoints
    print(f"\n{BLUE}Testing WebSocket Endpoints (2 total)...{RESET}\n")
    
    await verifier.test_websocket("/ws/live", "1. WebSocket /ws/live")
    await verifier.test_websocket("/ws/live/latest", "2. WebSocket /ws/live/latest")
    
    verifier.print_section("WEBSOCKET ENDPOINTS", verifier.ws_results)
    
    # Test Redis caching
    print(f"\n{BLUE}Testing Redis Caching...{RESET}\n")
    
    verifier.test_redis_cache()
    
    verifier.print_section("REDIS CACHING", verifier.cache_results)
    
    # Test request ID propagation
    print(f"\n{BLUE}Testing Request ID Propagation...{RESET}\n")
    
    await verifier.test_request_id_propagation()
    
    verifier.print_section("REQUEST ID PROPAGATION", verifier.request_id_results)
    
    # Print summary
    success = verifier.print_summary()
    
    if success:
        print(f"{GREEN}✓ All backend components verified successfully!{RESET}\n")
        return 0
    else:
        print(f"{YELLOW}⚠ Some components need attention. Review details above.{RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
