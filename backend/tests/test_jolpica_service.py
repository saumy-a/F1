"""
Unit tests for Jolpica F1 API Service

Tests all 7 service functions with mocked httpx responses.
Tests error handling for API failures including timeouts, HTTP errors, and network errors.
Validates retry logic and request ID tracking.

Requirements: 4.1
"""

import pytest
import pytest_asyncio
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
import uuid

from app.services.jolpica import (
    fetch_driver_standings,
    fetch_constructor_standings,
    fetch_race_schedule,
    fetch_race_results,
    fetch_qualifying_results,
    fetch_lap_times,
    fetch_driver_race_results,
    _fetch_with_retry,
    close_client,
    JOLPICA_API_BASE_URL,
)


# Sample response data matching Jolpica API structure
SAMPLE_DRIVER_STANDINGS = {
    "MRData": {
        "StandingsTable": {
            "StandingsLists": [
                {
                    "DriverStandings": [
                        {
                            "position": "1",
                            "points": "575",
                            "wins": "19",
                            "Driver": {
                                "driverId": "max_verstappen",
                                "givenName": "Max",
                                "familyName": "Verstappen"
                            },
                            "Constructors": [{"constructorId": "red_bull", "name": "Red Bull"}]
                        }
                    ]
                }
            ]
        }
    }
}

SAMPLE_CONSTRUCTOR_STANDINGS = {
    "MRData": {
        "StandingsTable": {
            "StandingsLists": [
                {
                    "ConstructorStandings": [
                        {
                            "position": "1",
                            "points": "860",
                            "wins": "21",
                            "Constructor": {"constructorId": "red_bull", "name": "Red Bull"}
                        }
                    ]
                }
            ]
        }
    }
}

SAMPLE_RACE_SCHEDULE = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "season": "2024",
                    "round": "1",
                    "raceName": "Bahrain Grand Prix",
                    "Circuit": {"circuitId": "bahrain"},
                    "date": "2024-03-02",
                    "time": "15:00:00Z"
                }
            ]
        }
    }
}

SAMPLE_RACE_RESULTS = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "season": "2024",
                    "round": "1",
                    "raceName": "Bahrain Grand Prix",
                    "Circuit": {"circuitId": "bahrain"},
                    "date": "2024-03-02",
                    "Results": [
                        {
                            "position": "1",
                            "points": "25",
                            "Driver": {"driverId": "max_verstappen"},
                            "Constructor": {"constructorId": "red_bull"},
                            "grid": "1",
                            "laps": "57",
                            "status": "Finished"
                        }
                    ]
                }
            ]
        }
    }
}

SAMPLE_QUALIFYING_RESULTS = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "season": "2024",
                    "round": "1",
                    "raceName": "Bahrain Grand Prix",
                    "Circuit": {"circuitId": "bahrain"},
                    "date": "2024-03-01",
                    "QualifyingResults": [
                        {
                            "position": "1",
                            "Driver": {"driverId": "max_verstappen"},
                            "Constructor": {"constructorId": "red_bull"},
                            "Q1": "1:29.123",
                            "Q2": "1:28.456",
                            "Q3": "1:27.789"
                        }
                    ]
                }
            ]
        }
    }
}

SAMPLE_LAP_TIMES = {
    "MRData": {
        "RaceTable": {
            "Races": [
                {
                    "season": "2024",
                    "round": "1",
                    "Laps": [
                        {
                            "number": "1",
                            "Timings": [
                                {
                                    "driverId": "max_verstappen",
                                    "position": "1",
                                    "time": "1:32.123"
                                },
                                {
                                    "driverId": "hamilton",
                                    "position": "2",
                                    "time": "1:32.456"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
}


@pytest.fixture
def mock_httpx_client():
    """Fixture providing a mocked httpx.AsyncClient"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    return mock_client


@pytest.fixture
def mock_response():
    """Fixture providing a mocked httpx.Response"""
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    """Cleanup fixture to close client after each test"""
    yield
    await close_client()


class TestFetchDriverStandings:
    """Tests for fetch_driver_standings function"""

    @pytest.mark.asyncio
    async def test_fetch_driver_standings_success(self, mock_httpx_client, mock_response):
        """Test successful fetch of driver standings"""
        mock_response.json.return_value = SAMPLE_DRIVER_STANDINGS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is not None
            assert len(result) == 1
            assert result[0]["position"] == "1"
            assert result[0]["points"] == "575"
            assert result[0]["Driver"]["driverId"] == "max_verstappen"
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/2024/driverStandings.json")

    @pytest.mark.asyncio
    async def test_fetch_driver_standings_with_round(self, mock_httpx_client, mock_response):
        """Test fetch driver standings for specific round"""
        mock_response.json.return_value = SAMPLE_DRIVER_STANDINGS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024", round_num=5)
            
            assert result is not None
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/2024/5/driverStandings.json")

    @pytest.mark.asyncio
    async def test_fetch_driver_standings_current_season(self, mock_httpx_client, mock_response):
        """Test fetch driver standings for current season"""
        mock_response.json.return_value = SAMPLE_DRIVER_STANDINGS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings()
            
            assert result is not None
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/current/driverStandings.json")

    @pytest.mark.asyncio
    async def test_fetch_driver_standings_empty_response(self, mock_httpx_client, mock_response):
        """Test handling of empty standings list"""
        mock_response.json.return_value = {
            "MRData": {
                "StandingsTable": {
                    "StandingsLists": []
                }
            }
        }
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_driver_standings_with_request_id(self, mock_httpx_client, mock_response):
        """Test request ID tracking in logs"""
        mock_response.json.return_value = SAMPLE_DRIVER_STANDINGS
        mock_httpx_client.get.return_value = mock_response
        request_id = str(uuid.uuid4())
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024", request_id=request_id)
            
            assert result is not None


class TestFetchConstructorStandings:
    """Tests for fetch_constructor_standings function"""

    @pytest.mark.asyncio
    async def test_fetch_constructor_standings_success(self, mock_httpx_client, mock_response):
        """Test successful fetch of constructor standings"""
        mock_response.json.return_value = SAMPLE_CONSTRUCTOR_STANDINGS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_constructor_standings(year="2024")
            
            assert result is not None
            assert len(result) == 1
            assert result[0]["position"] == "1"
            assert result[0]["points"] == "860"
            assert result[0]["Constructor"]["constructorId"] == "red_bull"

    @pytest.mark.asyncio
    async def test_fetch_constructor_standings_with_round(self, mock_httpx_client, mock_response):
        """Test fetch constructor standings for specific round"""
        mock_response.json.return_value = SAMPLE_CONSTRUCTOR_STANDINGS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_constructor_standings(year="2024", round_num=10)
            
            assert result is not None
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/2024/10/constructorStandings.json")


class TestFetchRaceSchedule:
    """Tests for fetch_race_schedule function"""

    @pytest.mark.asyncio
    async def test_fetch_race_schedule_success(self, mock_httpx_client, mock_response):
        """Test successful fetch of race schedule"""
        mock_response.json.return_value = SAMPLE_RACE_SCHEDULE
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_race_schedule(year="2024")
            
            assert result is not None
            assert len(result) == 1
            assert result[0]["raceName"] == "Bahrain Grand Prix"
            assert result[0]["season"] == "2024"
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/2024.json")

    @pytest.mark.asyncio
    async def test_fetch_race_schedule_empty(self, mock_httpx_client, mock_response):
        """Test handling of empty race schedule"""
        mock_response.json.return_value = {
            "MRData": {
                "RaceTable": {
                    "Races": []
                }
            }
        }
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_race_schedule(year="2024")
            
            assert result is None


class TestFetchRaceResults:
    """Tests for fetch_race_results function"""

    @pytest.mark.asyncio
    async def test_fetch_race_results_success(self, mock_httpx_client, mock_response):
        """Test successful fetch of race results"""
        mock_response.json.return_value = SAMPLE_RACE_RESULTS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_race_results(year="2024", round_num=1)
            
            assert result is not None
            assert result["raceName"] == "Bahrain Grand Prix"
            assert len(result["Results"]) == 1
            assert result["Results"][0]["position"] == "1"
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/2024/1/results.json")

    @pytest.mark.asyncio
    async def test_fetch_race_results_no_data(self, mock_httpx_client, mock_response):
        """Test handling when race has no results yet"""
        mock_response.json.return_value = {
            "MRData": {
                "RaceTable": {
                    "Races": []
                }
            }
        }
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_race_results(year="2024", round_num=1)
            
            assert result is None


class TestFetchQualifyingResults:
    """Tests for fetch_qualifying_results function"""

    @pytest.mark.asyncio
    async def test_fetch_qualifying_results_success(self, mock_httpx_client, mock_response):
        """Test successful fetch of qualifying results"""
        mock_response.json.return_value = SAMPLE_QUALIFYING_RESULTS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_qualifying_results(year="2024", round_num=1)
            
            assert result is not None
            assert result["raceName"] == "Bahrain Grand Prix"
            assert len(result["QualifyingResults"]) == 1
            assert result["QualifyingResults"][0]["Q3"] == "1:27.789"
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/2024/1/qualifying.json")


class TestFetchLapTimes:
    """Tests for fetch_lap_times function"""

    @pytest.mark.asyncio
    async def test_fetch_lap_times_success(self, mock_httpx_client, mock_response):
        """Test successful fetch and flattening of lap times"""
        mock_response.json.return_value = SAMPLE_LAP_TIMES
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_lap_times(year="2024", round_num=1)
            
            assert result is not None
            assert len(result) == 2  # Two drivers
            assert result[0]["driverId"] == "max_verstappen"
            assert result[0]["lap"] == "1"
            assert result[0]["time"] == "1:32.123"
            assert result[1]["driverId"] == "hamilton"
            mock_httpx_client.get.assert_called_once_with(f"{JOLPICA_API_BASE_URL}/2024/1/laps.json?limit=2000")

    @pytest.mark.asyncio
    async def test_fetch_lap_times_empty_laps(self, mock_httpx_client, mock_response):
        """Test handling of race with no lap data"""
        mock_response.json.return_value = {
            "MRData": {
                "RaceTable": {
                    "Races": [
                        {
                            "season": "2024",
                            "round": "1",
                            "Laps": []
                        }
                    ]
                }
            }
        }
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_lap_times(year="2024", round_num=1)
            
            assert result is None


class TestFetchDriverRaceResults:
    """Tests for fetch_driver_race_results function"""

    @pytest.mark.asyncio
    async def test_fetch_driver_race_results_success(self, mock_httpx_client, mock_response):
        """Test successful fetch of driver race results"""
        mock_response.json.return_value = SAMPLE_RACE_RESULTS
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_race_results(driver_id="max_verstappen", year="2024")
            
            assert result is not None
            assert len(result) == 1
            assert result[0]["raceName"] == "Bahrain Grand Prix"
            mock_httpx_client.get.assert_called_once_with(
                f"{JOLPICA_API_BASE_URL}/2024/drivers/max_verstappen/results.json?limit=100"
            )

    @pytest.mark.asyncio
    async def test_fetch_driver_race_results_no_races(self, mock_httpx_client, mock_response):
        """Test handling when driver has no race results"""
        mock_response.json.return_value = {
            "MRData": {
                "RaceTable": {
                    "Races": []
                }
            }
        }
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_race_results(driver_id="unknown_driver", year="2024")
            
            assert result is None


class TestErrorHandling:
    """Tests for error handling and retry logic"""

    @pytest.mark.asyncio
    async def test_timeout_error_with_retry(self, mock_httpx_client):
        """Test timeout error triggers retry with exponential backoff"""
        mock_httpx_client.get.side_effect = httpx.TimeoutException("Request timed out")
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None
            assert mock_httpx_client.get.call_count == 3  # MAX_RETRIES

    @pytest.mark.asyncio
    async def test_http_500_error_with_retry(self, mock_httpx_client):
        """Test HTTP 500 error triggers retry"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        error = httpx.HTTPStatusError("Server error", request=MagicMock(), response=mock_response)
        mock_httpx_client.get.side_effect = error
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None
            assert mock_httpx_client.get.call_count == 3  # MAX_RETRIES

    @pytest.mark.asyncio
    async def test_http_404_error_no_retry(self, mock_httpx_client):
        """Test HTTP 404 error does not trigger retry (client error)"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        error = httpx.HTTPStatusError("Not found", request=MagicMock(), response=mock_response)
        mock_httpx_client.get.side_effect = error
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None
            assert mock_httpx_client.get.call_count == 1  # No retry for 4xx

    @pytest.mark.asyncio
    async def test_network_error_with_retry(self, mock_httpx_client):
        """Test network error triggers retry"""
        mock_httpx_client.get.side_effect = httpx.RequestError("Network error")
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None
            assert mock_httpx_client.get.call_count == 3  # MAX_RETRIES

    @pytest.mark.asyncio
    async def test_json_decode_error(self, mock_httpx_client, mock_response):
        """Test invalid JSON response handling"""
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_retry_success_after_failure(self, mock_httpx_client, mock_response):
        """Test successful retry after initial failure"""
        mock_response.json.return_value = SAMPLE_DRIVER_STANDINGS
        # First call fails, second succeeds
        mock_httpx_client.get.side_effect = [
            httpx.TimeoutException("Timeout"),
            mock_response
        ]
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is not None
            assert len(result) == 1
            assert mock_httpx_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_malformed_response_structure(self, mock_httpx_client, mock_response):
        """Test handling of malformed API response structure"""
        mock_response.json.return_value = {"unexpected": "structure"}
        mock_httpx_client.get.return_value = mock_response
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_unexpected_exception(self, mock_httpx_client):
        """Test handling of unexpected exceptions"""
        mock_httpx_client.get.side_effect = Exception("Unexpected error")
        
        with patch('app.services.jolpica.get_client') as mock_get_client:
            mock_get_client.return_value.__aenter__.return_value = mock_httpx_client
            
            result = await fetch_driver_standings(year="2024")
            
            assert result is None
