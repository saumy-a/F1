"""
Property-based tests for standings endpoints.

Property 2: Position ordering
Validates: Requirements 2.1
Test that standings positions are always sequential and unique.
"""
import pytest
from hypothesis import given, strategies as st, settings
import httpx


# Use the running server for tests
BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
@given(
    year=st.sampled_from(["2020", "2021", "2022", "2023"]),
    round_num=st.one_of(st.none(), st.integers(min_value=1, max_value=22))
)
@settings(max_examples=20, deadline=15000)  # Increased deadline for API calls
async def test_driver_standings_position_ordering(year: str, round_num):
    """
    Property: Driver standings positions must be sequential starting from 1 and unique.
    
    For any valid year and round, the standings should have:
    - Positions starting at 1
    - No gaps in position numbers (1, 2, 3, ...)
    - No duplicate positions
    - Positions as strings (API format)
    """
    async with httpx.AsyncClient() as client:
        # Build URL with optional round parameter
        url = f"{BASE_URL}/api/standings/drivers/{year}"
        if round_num is not None:
            url += f"?round={round_num}"
        
        response = await client.get(url, timeout=10.0)
        
        # Skip if no data available (404 is acceptable for some year/round combinations)
        if response.status_code == 404:
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        standings = response.json()
        
        # Property: Standings should not be empty
        assert len(standings) > 0, "Standings should contain at least one entry"
        
        # Extract positions and convert to integers
        positions = [int(entry["position"]) for entry in standings]
        
        # Property 1: Positions should start at 1
        assert positions[0] == 1, f"First position should be 1, got {positions[0]}"
        
        # Property 2: Positions should be sequential (no gaps)
        expected_positions = list(range(1, len(positions) + 1))
        assert positions == expected_positions, \
            f"Positions should be sequential from 1 to {len(positions)}, got {positions}"
        
        # Property 3: All positions should be unique (no duplicates)
        assert len(positions) == len(set(positions)), \
            f"Positions should be unique, found duplicates in {positions}"
        
        # Property 4: Positions should be strings in the response
        for entry in standings:
            assert isinstance(entry["position"], str), \
                f"Position should be string, got {type(entry['position'])}"


@pytest.mark.asyncio
@given(
    year=st.sampled_from(["2020", "2021", "2022", "2023"]),
    round_num=st.one_of(st.none(), st.integers(min_value=1, max_value=22))
)
@settings(max_examples=20, deadline=15000)
async def test_constructor_standings_position_ordering(year: str, round_num):
    """
    Property: Constructor standings positions must be sequential starting from 1 and unique.
    
    For any valid year and round, the standings should have:
    - Positions starting at 1
    - No gaps in position numbers (1, 2, 3, ...)
    - No duplicate positions
    - Positions as strings (API format)
    """
    async with httpx.AsyncClient() as client:
        # Build URL with optional round parameter
        url = f"{BASE_URL}/api/standings/constructors/{year}"
        if round_num is not None:
            url += f"?round={round_num}"
        
        response = await client.get(url, timeout=10.0)
        
        # Skip if no data available (404 is acceptable for some year/round combinations)
        if response.status_code == 404:
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        standings = response.json()
        
        # Property: Standings should not be empty
        assert len(standings) > 0, "Standings should contain at least one entry"
        
        # Extract positions and convert to integers
        positions = [int(entry["position"]) for entry in standings]
        
        # Property 1: Positions should start at 1
        assert positions[0] == 1, f"First position should be 1, got {positions[0]}"
        
        # Property 2: Positions should be sequential (no gaps)
        expected_positions = list(range(1, len(positions) + 1))
        assert positions == expected_positions, \
            f"Positions should be sequential from 1 to {len(positions)}, got {positions}"
        
        # Property 3: All positions should be unique (no duplicates)
        assert len(positions) == len(set(positions)), \
            f"Positions should be unique, found duplicates in {positions}"
        
        # Property 4: Positions should be strings in the response
        for entry in standings:
            assert isinstance(entry["position"], str), \
                f"Position should be string, got {type(entry['position'])}"


@pytest.mark.asyncio
async def test_driver_standings_points_ordering():
    """
    Property: Driver standings should be ordered by points (descending).
    
    Higher positions should have equal or more points than lower positions.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/standings/drivers/2023", timeout=10.0)
        assert response.status_code == 200
        
        standings = response.json()
        points = [int(entry["points"]) for entry in standings]
        
        # Property: Points should be in descending order
        for i in range(len(points) - 1):
            assert points[i] >= points[i + 1], \
                f"Points should be descending: position {i+1} has {points[i]} points, " \
                f"position {i+2} has {points[i+1]} points"


@pytest.mark.asyncio
async def test_constructor_standings_points_ordering():
    """
    Property: Constructor standings should be ordered by points (descending).
    
    Higher positions should have equal or more points than lower positions.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/standings/constructors/2023", timeout=10.0)
        assert response.status_code == 200
        
        standings = response.json()
        points = [int(entry["points"]) for entry in standings]
        
        # Property: Points should be in descending order
        for i in range(len(points) - 1):
            assert points[i] >= points[i+1], \
                f"Points should be descending: position {i+1} has {points[i]} points, " \
                f"position {i+2} has {points[i+1]} points"
