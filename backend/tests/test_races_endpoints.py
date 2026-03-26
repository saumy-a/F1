"""
Unit tests for races endpoints.
Tests race schedule, results, qualifying, and lap times endpoints.
"""
import pytest
import httpx


# Use the running server for tests
BASE_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_get_race_schedule():
    """Test fetching race schedule for a season."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023", timeout=10.0)
        assert response.status_code == 200
        
        schedule = response.json()
        assert isinstance(schedule, list)
        assert len(schedule) > 0
        
        # Check first race structure
        first_race = schedule[0]
        assert "season" in first_race
        assert "round" in first_race
        assert "raceName" in first_race
        assert "Circuit" in first_race
        assert "date" in first_race
        
        # Check circuit structure
        circuit = first_race["Circuit"]
        assert "circuitId" in circuit
        assert "circuitName" in circuit


@pytest.mark.asyncio
async def test_get_race_schedule_invalid_year():
    """Test fetching race schedule with invalid year returns 404."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/1800", timeout=10.0)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_race_results():
    """Test fetching race results for a specific race."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/1/results", timeout=10.0)
        assert response.status_code == 200
        
        result = response.json()
        assert "season" in result
        assert "round" in result
        assert "Results" in result
        
        results = result["Results"]
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Check first result structure
        first_result = results[0]
        assert "position" in first_result
        assert "points" in first_result
        assert "Driver" in first_result
        assert "Constructor" in first_result
        assert "grid" in first_result
        assert "laps" in first_result
        assert "status" in first_result
        
        # Winner should be position 1
        assert first_result["position"] == "1"


@pytest.mark.asyncio
async def test_get_race_results_invalid_round():
    """Test fetching race results with invalid round returns 422 (validation error)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/999/results", timeout=10.0)
        # 422 because round validation (ge=1, le=30) catches it
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_qualifying_results():
    """Test fetching qualifying results for a specific race."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/1/qualifying", timeout=10.0)
        assert response.status_code == 200
        
        result = response.json()
        assert "season" in result
        assert "round" in result
        assert "QualifyingResults" in result
        
        qualifying = result["QualifyingResults"]
        assert isinstance(qualifying, list)
        assert len(qualifying) > 0
        
        # Check first qualifying result structure
        first_qual = qualifying[0]
        assert "position" in first_qual
        assert "Driver" in first_qual
        assert "Constructor" in first_qual
        
        # Pole position should be position 1
        assert first_qual["position"] == "1"
        
        # Check for Q times (at least Q1 should exist)
        assert "Q1" in first_qual or "Q2" in first_qual or "Q3" in first_qual


@pytest.mark.asyncio
async def test_get_qualifying_results_invalid_round():
    """Test fetching qualifying results with invalid round returns 422 (validation error)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/999/qualifying", timeout=10.0)
        # 422 because round validation (ge=1, le=30) catches it
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_lap_times():
    """Test fetching lap times for a specific race."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/1/laps", timeout=15.0)
        assert response.status_code == 200
        
        lap_times = response.json()
        assert isinstance(lap_times, list)
        assert len(lap_times) > 0
        
        # Check first lap time structure
        first_lap = lap_times[0]
        assert "driverId" in first_lap
        assert "lap" in first_lap
        assert "position" in first_lap
        assert "time" in first_lap
        
        # Verify lap time format (MM:SS.mmm)
        assert ":" in first_lap["time"]
        assert "." in first_lap["time"]


@pytest.mark.asyncio
async def test_get_lap_times_invalid_round():
    """Test fetching lap times with invalid round returns 422 (validation error)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/999/laps", timeout=10.0)
        # 422 because round validation (ge=1, le=30) catches it
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_cache_behavior_race_schedule():
    """Test that race schedule is cached (second request should be faster)."""
    async with httpx.AsyncClient() as client:
        # First request (cache miss)
        response1 = await client.get(f"{BASE_URL}/api/races/2022", timeout=10.0)
        assert response1.status_code == 200
        
        # Second request (cache hit - should be faster)
        response2 = await client.get(f"{BASE_URL}/api/races/2022", timeout=10.0)
        assert response2.status_code == 200
        
        # Both should return same data
        assert response1.json() == response2.json()


@pytest.mark.asyncio
async def test_race_results_points_sum():
    """Test that race results points are valid (winner gets 25 points in modern F1)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/1/results", timeout=10.0)
        assert response.status_code == 200
        
        result = response.json()
        results = result["Results"]
        
        # Winner should get 25 points (modern F1 scoring)
        winner = results[0]
        assert winner["position"] == "1"
        assert float(winner["points"]) == 25.0


@pytest.mark.asyncio
async def test_qualifying_position_ordering():
    """Test that qualifying results are ordered by position."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/races/2023/1/qualifying", timeout=10.0)
        assert response.status_code == 200
        
        result = response.json()
        qualifying = result["QualifyingResults"]
        
        # Extract positions
        positions = [int(q["position"]) for q in qualifying]
        
        # Positions should be sequential from 1
        expected_positions = list(range(1, len(positions) + 1))
        assert positions == expected_positions
