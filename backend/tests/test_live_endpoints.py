"""
Unit tests for live data API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, ANY
from datetime import datetime, timedelta, timezone
from app.main import app

client = TestClient(app)


# Mock Data
MOCK_SESSION = {
    "session_key": "9158",
    "session_name": "Race",
    "session_type": "Race",
    "date_start": "2024-03-10T14:00:00Z",
    "date_end": "2024-03-10T16:00:00Z",
    "gmt_offset": "+03:00",
    "location": "Jeddah",
    "country_name": "Saudi Arabia",
    "circuit_short_name": "Jeddah"
}

MOCK_DRIVERS = [
    {
        "driver_number": 1,
        "broadcast_name": "M VERSTAPPEN",
        "full_name": "Max Verstappen",
        "name_acronym": "VER",
        "team_name": "Red Bull Racing",
        "team_colour": "3671C6"
    },
    {
        "driver_number": 44,
        "broadcast_name": "L HAMILTON",
        "full_name": "Lewis Hamilton",
        "name_acronym": "HAM",
        "team_name": "Mercedes",
        "team_colour": "27F4D2"
    }
]

MOCK_POSITIONS = [
    {"driver_number": 1, "position": 1, "date": "2024-03-10T14:30:00Z"},
    {"driver_number": 44, "position": 2, "date": "2024-03-10T14:30:00Z"}
]

MOCK_INTERVALS = [
    {"driver_number": 1, "gap_to_leader": "0.000", "interval": "0.000", "date": "2024-03-10T14:30:00Z"},
    {"driver_number": 44, "gap_to_leader": "2.345", "interval": "2.345", "date": "2024-03-10T14:30:00Z"}
]

MOCK_STINTS = [
    {
        "driver_number": 1,
        "stint_number": 1,
        "compound": "SOFT",
        "tyre_age_at_start": 0,
        "lap_start": 1,
        "lap_end": 15
    },
    {
        "driver_number": 44,
        "stint_number": 1,
        "compound": "MEDIUM",
        "tyre_age_at_start": 0,
        "lap_start": 1,
        "lap_end": 20
    }
]

MOCK_PITS = [
    {
        "driver_number": 1,
        "lap_number": 15,
        "pit_duration": 2.3,
        "date": "2024-03-10T14:45:00Z"
    }
]

MOCK_WEATHER = {
    "air_temperature": 28.5,
    "track_temperature": 42.3,
    "humidity": 45,
    "pressure": 1013.2,
    "rainfall": 0,
    "wind_direction": 180,
    "wind_speed": 3.5,
    "date": "2024-03-10T14:30:00Z"
}

MOCK_RACE_CONTROL = [
    {
        "category": "Flag",
        "message": "GREEN FLAG",
        "date": "2024-03-10T14:00:00Z",
        "lap_number": 1,
        "driver_number": None,
        "flag": "GREEN"
    }
]

MOCK_RADIO = [
    {
        "driver_number": 1,
        "date": "2024-03-10T14:30:00Z",
        "recording_url": "https://example.com/radio.mp3",
        "duration": 5.2
    }
]


class TestSessionEndpoint:
    """Test suite for /api/live/session endpoint."""
    
    @patch('app.routers.live.fetch_current_session', new_callable=AsyncMock)
    def test_get_current_session_live_mode(self, mock_fetch):
        """Test /api/live/session returns correct mode for live scenario."""
        # Create a session that is currently live
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=30)
        end_time = now + timedelta(minutes=90)
        
        session = MOCK_SESSION.copy()
        session["date_start"] = start_time.isoformat().replace("+00:00", "Z")
        session["date_end"] = end_time.isoformat().replace("+00:00", "Z")
        mock_fetch.return_value = session
        
        response = client.get("/api/live/session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_key"] == "9158"
        assert data["session_name"] == "Race"
        assert data["mode"] == "live"
    
    @patch('app.routers.live.fetch_current_session', new_callable=AsyncMock)
    def test_get_current_session_upcoming_mode(self, mock_fetch):
        """Test /api/live/session returns correct mode for upcoming scenario."""
        # Create a session that starts in the future
        now = datetime.now(timezone.utc)
        start_time = now + timedelta(hours=2)
        end_time = start_time + timedelta(hours=2)
        
        session = MOCK_SESSION.copy()
        session["date_start"] = start_time.isoformat().replace("+00:00", "Z")
        session["date_end"] = end_time.isoformat().replace("+00:00", "Z")
        mock_fetch.return_value = session
        
        response = client.get("/api/live/session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "upcoming"
    
    @patch('app.routers.live.fetch_current_session', new_callable=AsyncMock)
    def test_get_current_session_replay_mode(self, mock_fetch):
        """Test /api/live/session returns correct mode for replay scenario."""
        # Create a session that ended in the past
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(hours=4)
        end_time = now - timedelta(hours=2)
        
        session = MOCK_SESSION.copy()
        session["date_start"] = start_time.isoformat().replace("+00:00", "Z")
        session["date_end"] = end_time.isoformat().replace("+00:00", "Z")
        mock_fetch.return_value = session
        
        response = client.get("/api/live/session")
        
        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == "replay"
    
    @patch('app.routers.live.fetch_current_session', new_callable=AsyncMock)
    def test_get_current_session_not_found(self, mock_fetch):
        """Test /api/live/session returns 404 when no session available."""
        mock_fetch.return_value = None
        
        response = client.get("/api/live/session")
        
        assert response.status_code == 404
        assert "No current session found" in response.json()["detail"]
    
    @patch('app.routers.live.fetch_current_session', new_callable=AsyncMock)
    def test_get_current_session_api_failure(self, mock_fetch):
        """Test /api/live/session returns 500 on OpenF1 API failure."""
        mock_fetch.side_effect = Exception("OpenF1 API connection failed")
        
        response = client.get("/api/live/session")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


class TestDataEndpointsWithPathParameters:
    """Test suite for live data endpoints with path parameters."""
    
    @patch('app.routers.live.fetch_live_positions', new_callable=AsyncMock)
    def test_get_positions_with_session_key(self, mock_positions):
        """Test /api/live/positions/{session_key} returns correct data structure."""
        mock_positions.return_value = MOCK_POSITIONS.copy()
        
        response = client.get("/api/live/positions/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["driver_number"] == 1
        assert data[0]["position"] == 1
        assert "date" in data[0]
        mock_positions.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_live_intervals', new_callable=AsyncMock)
    def test_get_intervals_with_session_key(self, mock_intervals):
        """Test /api/live/intervals/{session_key} returns correct data structure."""
        mock_intervals.return_value = MOCK_INTERVALS.copy()
        
        response = client.get("/api/live/intervals/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["driver_number"] == 1
        assert data[0]["gap_to_leader"] == "0.000"
        assert data[0]["interval"] == "0.000"
        assert "date" in data[0]
        mock_intervals.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_live_stints', new_callable=AsyncMock)
    def test_get_stints_with_session_key(self, mock_stints):
        """Test /api/live/stints/{session_key} returns correct data structure."""
        mock_stints.return_value = MOCK_STINTS.copy()
        
        response = client.get("/api/live/stints/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["driver_number"] == 1
        assert data[0]["compound"] == "SOFT"
        assert data[0]["lap_start"] == 1
        assert data[0]["lap_end"] == 15
        mock_stints.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_live_pits', new_callable=AsyncMock)
    def test_get_pits_with_session_key(self, mock_pits):
        """Test /api/live/pits/{session_key} returns correct data structure."""
        mock_pits.return_value = MOCK_PITS.copy()
        
        response = client.get("/api/live/pits/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["driver_number"] == 1
        assert data[0]["lap_number"] == 15
        assert data[0]["pit_duration"] == 2.3
        mock_pits.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_live_weather', new_callable=AsyncMock)
    def test_get_weather_with_session_key(self, mock_weather):
        """Test /api/live/weather/{session_key} returns correct data structure."""
        mock_weather.return_value = MOCK_WEATHER.copy()
        
        response = client.get("/api/live/weather/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert data["air_temperature"] == 28.5
        assert data["track_temperature"] == 42.3
        assert data["humidity"] == 45
        assert data["pressure"] == 1013.2
        assert data["rainfall"] == 0
        assert data["wind_direction"] == 180
        assert data["wind_speed"] == 3.5
        assert "date" in data
        mock_weather.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_live_weather', new_callable=AsyncMock)
    def test_get_weather_not_found(self, mock_weather):
        """Test /api/live/weather/{session_key} returns 404 when no weather data available."""
        mock_weather.return_value = None
        
        response = client.get("/api/live/weather/9158")
        
        assert response.status_code == 404
        assert "No weather data available" in response.json()["detail"]
    
    @patch('app.routers.live.fetch_live_racecontrol', new_callable=AsyncMock)
    def test_get_race_control_with_session_key(self, mock_race_control):
        """Test /api/live/race-control/{session_key} returns correct data structure."""
        mock_race_control.return_value = MOCK_RACE_CONTROL.copy()
        
        response = client.get("/api/live/race-control/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Flag"
        assert data[0]["message"] == "GREEN FLAG"
        assert data[0]["flag"] == "GREEN"
        assert "date" in data[0]
        mock_race_control.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_live_radio', new_callable=AsyncMock)
    def test_get_radio_with_session_key(self, mock_radio):
        """Test /api/live/radio/{session_key} returns correct data structure."""
        mock_radio.return_value = MOCK_RADIO.copy()
        
        response = client.get("/api/live/radio/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["driver_number"] == 1
        assert data[0]["recording_url"] == "https://example.com/radio.mp3"
        assert data[0]["duration"] == 5.2
        mock_radio.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_starting_grid', new_callable=AsyncMock)
    def test_get_starting_grid_with_session_key(self, mock_grid):
        """Test /api/live/grid/{session_key} returns correct data structure."""
        mock_grid.return_value = MOCK_POSITIONS.copy()
        
        response = client.get("/api/live/grid/9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["driver_number"] == 1
        assert data[0]["position"] == 1
        mock_grid.assert_called_once_with("9158", request_id=ANY)
    
    @patch('app.routers.live.fetch_starting_grid', new_callable=AsyncMock)
    def test_get_starting_grid_not_found(self, mock_grid):
        """Test /api/live/grid/{session_key} returns 404 when no grid data available."""
        mock_grid.return_value = None
        
        response = client.get("/api/live/grid/9158")
        
        assert response.status_code == 404
        assert "No starting grid data available" in response.json()["detail"]


class TestDriversEndpoint:
    """Test suite for /api/live/drivers endpoint."""
    
    @patch('app.routers.live.fetch_session_drivers', new_callable=AsyncMock)
    @patch('app.routers.live.fetch_current_session', new_callable=AsyncMock)
    def test_get_drivers_without_session_key(self, mock_session, mock_drivers):
        """Test /api/live/drivers fetches current session when no key provided."""
        mock_session.return_value = MOCK_SESSION.copy()
        mock_drivers.return_value = MOCK_DRIVERS.copy()
        
        response = client.get("/api/live/drivers")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["driver_number"] == 1
        assert data[0]["name_acronym"] == "VER"
        assert data[0]["team_name"] == "Red Bull Racing"
    
    @patch('app.routers.live.fetch_session_drivers', new_callable=AsyncMock)
    def test_get_drivers_with_session_key(self, mock_drivers):
        """Test /api/live/drivers with explicit session key."""
        mock_drivers.return_value = MOCK_DRIVERS.copy()
        
        response = client.get("/api/live/drivers?session_key=9158")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        mock_drivers.assert_called_once_with("9158", request_id=ANY)


class TestSessionsEndpoint:
    """Test suite for /api/live/sessions endpoint."""
    
    @patch('app.routers.live.fetch_sessions_by_year', new_callable=AsyncMock)
    def test_get_sessions_by_year(self, mock_sessions):
        """Test /api/live/sessions returns list of sessions for a year."""
        # Create multiple sessions with different times
        now = datetime.now(timezone.utc)
        sessions = [
            {
                **MOCK_SESSION,
                "session_key": "9158",
                "date_start": (now - timedelta(days=30)).isoformat().replace("+00:00", "Z"),
                "date_end": (now - timedelta(days=30, hours=-2)).isoformat().replace("+00:00", "Z")
            },
            {
                **MOCK_SESSION,
                "session_key": "9159",
                "date_start": (now + timedelta(days=7)).isoformat().replace("+00:00", "Z"),
                "date_end": (now + timedelta(days=7, hours=2)).isoformat().replace("+00:00", "Z")
            }
        ]
        mock_sessions.return_value = sessions
        
        response = client.get("/api/live/sessions?year=2024")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("mode" in session for session in data)
        assert data[0]["mode"] == "replay"  # Past session
        assert data[1]["mode"] == "upcoming"  # Future session
        mock_sessions.assert_called_once_with(2024, request_id=ANY)


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    @patch('app.routers.live.fetch_live_positions', new_callable=AsyncMock)
    def test_positions_endpoint_internal_error(self, mock_positions):
        """Test /api/live/positions/{session_key} returns 500 on internal error."""
        mock_positions.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/live/positions/9158")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    @patch('app.routers.live.fetch_live_intervals', new_callable=AsyncMock)
    def test_intervals_endpoint_internal_error(self, mock_intervals):
        """Test /api/live/intervals/{session_key} returns 500 on internal error."""
        mock_intervals.side_effect = Exception("Network timeout")
        
        response = client.get("/api/live/intervals/9158")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    @patch('app.routers.live.fetch_live_weather', new_callable=AsyncMock)
    def test_weather_endpoint_internal_error(self, mock_weather):
        """Test /api/live/weather/{session_key} returns 500 on internal error."""
        mock_weather.side_effect = Exception("API unavailable")
        
        response = client.get("/api/live/weather/9158")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    
    @patch('app.routers.live.fetch_live_racecontrol', new_callable=AsyncMock)
    def test_race_control_endpoint_internal_error(self, mock_race_control):
        """Test /api/live/race-control/{session_key} returns 500 on internal error."""
        mock_race_control.side_effect = Exception("Service unavailable")
        
        response = client.get("/api/live/race-control/9158")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


class TestEmptyDataResponses:
    """Test suite for endpoints returning empty data."""
    
    @patch('app.routers.live.fetch_live_positions', new_callable=AsyncMock)
    def test_positions_empty_list(self, mock_positions):
        """Test /api/live/positions/{session_key} returns empty list when no data."""
        mock_positions.return_value = []
        
        response = client.get("/api/live/positions/9158")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.routers.live.fetch_live_intervals', new_callable=AsyncMock)
    def test_intervals_empty_list(self, mock_intervals):
        """Test /api/live/intervals/{session_key} returns empty list when no data."""
        mock_intervals.return_value = []
        
        response = client.get("/api/live/intervals/9158")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.routers.live.fetch_live_stints', new_callable=AsyncMock)
    def test_stints_empty_list(self, mock_stints):
        """Test /api/live/stints/{session_key} returns empty list when no data."""
        mock_stints.return_value = []
        
        response = client.get("/api/live/stints/9158")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.routers.live.fetch_live_pits', new_callable=AsyncMock)
    def test_pits_empty_list(self, mock_pits):
        """Test /api/live/pits/{session_key} returns empty list when no data."""
        mock_pits.return_value = []
        
        response = client.get("/api/live/pits/9158")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.routers.live.fetch_live_racecontrol', new_callable=AsyncMock)
    def test_race_control_empty_list(self, mock_race_control):
        """Test /api/live/race-control/{session_key} returns empty list when no data."""
        mock_race_control.return_value = []
        
        response = client.get("/api/live/race-control/9158")
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('app.routers.live.fetch_live_radio', new_callable=AsyncMock)
    def test_radio_empty_list(self, mock_radio):
        """Test /api/live/radio/{session_key} returns empty list when no data."""
        mock_radio.return_value = []
        
        response = client.get("/api/live/radio/9158")
        
        assert response.status_code == 200
        assert response.json() == []


class TestSessionModeLogic:
    """Test session mode determination logic."""
    
    def test_determine_mode_live(self):
        """Test live session mode when current time is between date_start and date_end."""
        from app.services.live import determine_session_mode
        from datetime import datetime, timedelta, timezone
        
        # Create a session that started 30 minutes ago and ends in 90 minutes
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=30)
        end_time = now + timedelta(minutes=90)
        
        session = {
            "date_start": start_time.isoformat(),
            "date_end": end_time.isoformat()
        }
        
        mode = determine_session_mode(session)
        assert mode == "live"
    
    def test_determine_mode_upcoming(self):
        """Test upcoming session mode when current time is before date_start."""
        from app.services.live import determine_session_mode
        from datetime import datetime, timedelta, timezone
        
        future_time = datetime.now(timezone.utc) + timedelta(hours=2)
        session = {
            "date_start": future_time.isoformat(),
            "date_end": (future_time + timedelta(hours=2)).isoformat()
        }
        
        mode = determine_session_mode(session)
        assert mode == "upcoming"
    
    def test_determine_mode_replay(self):
        """Test replay session mode when current time is after date_end."""
        from app.services.live import determine_session_mode
        from datetime import datetime, timedelta, timezone
        
        past_time = datetime.now(timezone.utc) - timedelta(hours=4)
        session = {
            "date_start": past_time.isoformat(),
            "date_end": (past_time + timedelta(hours=2)).isoformat()
        }
        
        mode = determine_session_mode(session)
        assert mode == "replay"
    
    def test_determine_mode_missing_date(self):
        """Test mode determination with missing date."""
        from app.services.live import determine_session_mode
        
        session = {}
        
        mode = determine_session_mode(session)
        assert mode == "replay"  # Default to replay on error
