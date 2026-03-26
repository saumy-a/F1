#!/usr/bin/env python3
"""
Comprehensive endpoint testing script for F1 Dashboard API
Tests all 22 REST endpoints and verifies responses
"""

import httpx
import asyncio
from typing import Dict, List, Tuple
import json

BASE_URL = "http://localhost:8000"

# ANSI color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class EndpointTester:
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.total = 0
        self.passed = 0
        self.failed = 0
    
    async def test_endpoint(self, method: str, path: str, description: str, 
                           expected_status: int = 200, check_fields: List[str] = None):
        """Test a single endpoint"""
        self.total += 1
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{path}")
                elif method == "POST":
                    response = await client.post(f"{BASE_URL}{path}", json={})
                
                # Check status code
                if response.status_code != expected_status:
                    self.failed += 1
                    self.results.append((description, False, 
                                       f"Expected {expected_status}, got {response.status_code}"))
                    return False
                
                # Check response fields if specified
                if check_fields and response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        data = data[0]
                    
                    missing_fields = [f for f in check_fields if f not in str(data)]
                    if missing_fields:
                        self.failed += 1
                        self.results.append((description, False, 
                                           f"Missing fields: {missing_fields}"))
                        return False
                
                self.passed += 1
                self.results.append((description, True, "OK"))
                return True
                
        except Exception as e:
            self.failed += 1
            self.results.append((description, False, str(e)))
            return False
    
    def print_results(self):
        """Print test results"""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}ENDPOINT TEST RESULTS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        for description, passed, message in self.results:
            status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
            print(f"{status} | {description}")
            if not passed:
                print(f"       {RED}Error: {message}{RESET}")
        
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"Total: {self.total} | {GREEN}Passed: {self.passed}{RESET} | {RED}Failed: {self.failed}{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        return self.failed == 0


async def main():
    tester = EndpointTester()
    
    print(f"{YELLOW}Testing F1 Dashboard API - All 22 REST Endpoints{RESET}\n")
    
    # Health check
    print(f"{BLUE}[1/22] Testing Health Check...{RESET}")
    await tester.test_endpoint("GET", "/health", "Health Check", 200, ["status"])
    
    # Standings endpoints (2)
    print(f"{BLUE}[2/22] Testing Driver Standings...{RESET}")
    await tester.test_endpoint("GET", "/api/standings/drivers/2024", 
                               "Driver Standings 2024", 200, ["position", "points"])
    
    print(f"{BLUE}[3/22] Testing Constructor Standings...{RESET}")
    await tester.test_endpoint("GET", "/api/standings/constructors/2024", 
                               "Constructor Standings 2024", 200, ["position", "points"])
    
    # Races endpoints (4)
    print(f"{BLUE}[4/22] Testing Race Schedule...{RESET}")
    await tester.test_endpoint("GET", "/api/races/2024", 
                               "Race Schedule 2024", 200, ["raceName", "Circuit"])
    
    print(f"{BLUE}[5/22] Testing Race Results...{RESET}")
    await tester.test_endpoint("GET", "/api/races/2024/1/results", 
                               "Race Results 2024 Round 1", 200, ["Results"])
    
    print(f"{BLUE}[6/22] Testing Qualifying Results...{RESET}")
    await tester.test_endpoint("GET", "/api/races/2024/1/qualifying", 
                               "Qualifying Results 2024 Round 1", 200, ["QualifyingResults"])
    
    print(f"{BLUE}[7/22] Testing Lap Times...{RESET}")
    await tester.test_endpoint("GET", "/api/races/2024/1/laps", 
                               "Lap Times 2024 Round 1", 200)
    
    # Analytics endpoints (7)
    print(f"{BLUE}[8/22] Testing Performance Trends...{RESET}")
    await tester.test_endpoint("GET", "/api/analytics/trends/verstappen/2024", 
                               "Performance Trends - Verstappen 2024", 200)
    
    print(f"{BLUE}[9/22] Testing Consistency Score...{RESET}")
    await tester.test_endpoint("GET", "/api/analytics/consistency/verstappen/2024", 
                               "Consistency Score - Verstappen 2024", 200, ["score"])
    
    print(f"{BLUE}[10/22] Testing Form Indicator...{RESET}")
    await tester.test_endpoint("GET", "/api/analytics/form/verstappen/2024", 
                               "Form Indicator - Verstappen 2024", 200, ["trend"])
    
    print(f"{BLUE}[11/22] Testing DNF Rate...{RESET}")
    await tester.test_endpoint("GET", "/api/analytics/dnf/verstappen/2024", 
                               "DNF Rate - Verstappen 2024", 200, ["dnf_rate"])
    
    print(f"{BLUE}[12/22] Testing Driver Comparison...{RESET}")
    await tester.test_endpoint("GET", "/api/analytics/compare?driver_ids=verstappen,hamilton&year=2024", 
                               "Driver Comparison", 200)
    
    print(f"{BLUE}[13/22] Testing Circuit Performance...{RESET}")
    await tester.test_endpoint("GET", "/api/analytics/circuit/monza?year=2024", 
                               "Circuit Performance - Monza", 200)
    
    print(f"{BLUE}[14/22] Testing Championship Projection...{RESET}")
    await tester.test_endpoint("GET", "/api/analytics/projection/2024", 
                               "Championship Projection 2024", 200)
    
    # Live data endpoints (8)
    print(f"{BLUE}[15/22] Testing Current Session...{RESET}")
    await tester.test_endpoint("GET", "/api/live/session", 
                               "Current Session Info", 200)
    
    print(f"{BLUE}[16/22] Testing Session Drivers...{RESET}")
    await tester.test_endpoint("GET", "/api/live/drivers?session_key=latest", 
                               "Session Drivers", 200)
    
    print(f"{BLUE}[17/22] Testing Live Positions...{RESET}")
    await tester.test_endpoint("GET", "/api/live/positions?session_key=latest", 
                               "Live Positions", 200)
    
    print(f"{BLUE}[18/22] Testing Live Intervals...{RESET}")
    await tester.test_endpoint("GET", "/api/live/intervals?session_key=latest", 
                               "Live Intervals", 200)
    
    print(f"{BLUE}[19/22] Testing Live Stints...{RESET}")
    await tester.test_endpoint("GET", "/api/live/stints?session_key=latest", 
                               "Live Stints", 200)
    
    print(f"{BLUE}[20/22] Testing Live Pit Stops...{RESET}")
    await tester.test_endpoint("GET", "/api/live/pits?session_key=latest", 
                               "Live Pit Stops", 200)
    
    print(f"{BLUE}[21/22] Testing Live Weather...{RESET}")
    await tester.test_endpoint("GET", "/api/live/weather?session_key=latest", 
                               "Live Weather", 200)
    
    print(f"{BLUE}[22/22] Testing Race Control Messages...{RESET}")
    await tester.test_endpoint("GET", "/api/live/racecontrol?session_key=latest", 
                               "Race Control Messages", 200)
    
    # Print results
    success = tester.print_results()
    
    if success:
        print(f"{GREEN}✓ All endpoints are working correctly!{RESET}\n")
        return 0
    else:
        print(f"{RED}✗ Some endpoints failed. Please review the errors above.{RESET}\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
