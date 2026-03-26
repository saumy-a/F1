"""
Unit tests for OpenF1 API client functions.
Tests the new functions added in Task 1.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.openf1 import (
    fetch_live_radio,
    fetch_sessions_by_year,
    fetch_starting_grid,
    get_http_client,
    close_http_client
)


# Mock Data
MOCK_RADIO = [
    {
        "driver_number": 1,
        "date": "2024-03-10T14:30:00Z",
        "recording_url": "https://example.com/radio1.mp3",
        "duration": 5.2
    },
    {
        "driver_number": 44,
        "date": "2024-03-10T14:32:00Z",
        "recording_url": "https://example.com/radio2.mp3",
        "duration": 3.8
    }
]

MOCK_SESSIONS = [
    {
        "session_key": "9158",
        "session_name": "Race",
        "session_type": "Race",
        "date_start": "2024-03-10T14:00:00Z",
        "date_end": "2024-03-10T16:00:00Z",
        "location": "Jeddah",
        "country_name": "Saudi Arabia",
        "circuit_short_name": "Jeddah"
    },
    {
        "session_key": "9157",
        "session_name": "Qualifying",
        "session_type": "Qualifying",
        "date_start": "2024-03-09T15:00:00Z",
        "date_end": "2024-03-09T16:00:00Z",
        "location": "Jeddah",
        "country_name": "Saudi Arabia",
        "circuit_short_name": "Jeddah"
    }
]

MOCK_POSITIONS = [
    {"driver_number": 1, "position": 1, "date": "2024-03-10T14:00:00Z"},
    {"driver_number": 44, "position": 2, "date": "2024-03-10T14:00:00Z"},
    {"driver_number": 1, "position": 1, "date": "2024-03-10T14:30:00Z"},
    {"driver_number": 44, "position": 3, "date": "2024-03-10T14:30:00Z"}
]


class TestOpenF1Client:
    """Test suite for OpenF1 API client functions."""
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_live_radio_success(self, mock_get_client):
        """Test successful team radio retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_RADIO.copy()
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_live_radio("9158", "test-request-id")
        
        assert len(result) == 2
        assert result[0]["driver_number"] == 1
        assert result[0]["recording_url"] == "https://example.com/radio1.mp3"
        assert result[1]["duration"] == 3.8
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_sessions_by_year_success(self, mock_get_client):
        """Test successful sessions by year retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_SESSIONS.copy()
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_sessions_by_year(2024, "test-request-id")
        
        assert len(result) == 2
        assert result[0]["session_name"] == "Race"
        assert result[1]["session_name"] == "Qualifying"
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_starting_grid_success(self, mock_get_client):
        """Test successful starting grid retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_POSITIONS.copy()
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_starting_grid("9158", "test-request-id")
        
        # Should return earliest positions (starting grid)
        assert len(result) == 2
        assert result[0]["position"] == 1
        assert result[0]["driver_number"] == 1
        assert result[1]["position"] == 2
        assert result[1]["driver_number"] == 44
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_live_radio_empty(self, mock_get_client):
        """Test team radio retrieval with no data."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_live_radio("9158", "test-request-id")
        
        assert result == []
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_sessions_by_year_error(self, mock_get_client):
        """Test sessions by year with API error."""
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=Exception("API Error"))
        mock_get_client.return_value = mock_client
        
        result = await fetch_sessions_by_year(2024, "test-request-id")
        
        assert result == []
    
    def test_http_client_singleton(self):
        """Test that get_http_client returns the same instance."""
        client1 = get_http_client()
        client2 = get_http_client()
        
        assert client1 is client2
    
    @pytest.mark.asyncio
    async def test_close_http_client(self):
        """Test closing the HTTP client."""
        # Get a client first
        client = get_http_client()
        assert client is not None
        
        # Close it
        await close_http_client()
        
        # Getting a new client should create a new instance
        new_client = get_http_client()
        assert new_client is not None
        assert new_client is not client


class TestOpenF1ClientErrorHandling:
    """Test suite for OpenF1 API client error handling."""
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_current_session_timeout(self, mock_get_client):
        """Test that fetch_current_session handles timeout errors gracefully."""
        import httpx
        from app.services.openf1 import fetch_current_session
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        mock_get_client.return_value = mock_client
        
        result = await fetch_current_session("test-request-id")
        
        # Should return None instead of raising exception
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_current_session_404(self, mock_get_client):
        """Test that fetch_current_session handles 404 errors gracefully."""
        import httpx
        from app.services.openf1 import fetch_current_session
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=404)
        )
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_current_session("test-request-id")
        
        # Should return None instead of raising exception
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_current_session_500(self, mock_get_client):
        """Test that fetch_current_session handles 500 errors gracefully."""
        import httpx
        from app.services.openf1 import fetch_current_session
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500)
        )
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_current_session("test-request-id")
        
        # Should return None instead of raising exception
        assert result is None
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_live_positions_timeout(self, mock_get_client):
        """Test that fetch_live_positions handles timeout errors gracefully."""
        import httpx
        from app.services.openf1 import fetch_live_positions
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timeout"))
        mock_get_client.return_value = mock_client
        
        result = await fetch_live_positions("9158", "test-request-id")
        
        # Should return empty list instead of raising exception
        assert result == []
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_live_intervals_404(self, mock_get_client):
        """Test that fetch_live_intervals handles 404 errors gracefully."""
        import httpx
        from app.services.openf1 import fetch_live_intervals
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=404)
        )
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_live_intervals("9158", "test-request-id")
        
        # Should return empty list instead of raising exception
        assert result == []
    
    @pytest.mark.asyncio
    @patch('app.services.openf1.get_http_client')
    async def test_fetch_live_weather_500(self, mock_get_client):
        """Test that fetch_live_weather handles 500 errors gracefully."""
        import httpx
        from app.services.openf1 import fetch_live_weather
        
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error",
            request=MagicMock(),
            response=MagicMock(status_code=500)
        )
        
        mock_client = MagicMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_get_client.return_value = mock_client
        
        result = await fetch_live_weather("9158", "test-request-id")
        
        # Should return None instead of raising exception
        assert result is None
