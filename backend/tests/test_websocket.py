"""
Integration tests for WebSocket endpoints.

Tests WebSocket connection, message reception, polling behavior,
and heartbeat mechanism.
"""
import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.ws.manager import ConnectionManager

# Use TestClient for WebSocket testing
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

MOCK_POSITIONS = [
    {"driver_number": 1, "position": 1, "date": "2024-03-10T14:30:00Z"},
    {"driver_number": 44, "position": 2, "date": "2024-03-10T14:30:00Z"}
]

MOCK_INTERVALS = [
    {"driver_number": 1, "gap_to_leader": "0.000", "interval": "0.000"},
    {"driver_number": 44, "gap_to_leader": "2.345", "interval": "2.345"}
]

MOCK_RACE_CONTROL = [
    {"category": "Flag", "message": "GREEN FLAG", "date": "2024-03-10T14:00:00Z"}
]


class TestWebSocketConnection:
    """Test WebSocket connection and basic functionality"""

    def test_websocket_rejects_invalid_session_key(self):
        """Test WebSocket rejects non-numeric session keys"""
        # Try to connect with invalid session key
        with pytest.raises(Exception):
            with client.websocket_connect("/ws/live/invalid_key") as websocket:
                pass

    @patch('app.services.openf1.fetch_live_positions')
    @patch('app.services.openf1.fetch_live_intervals')
    @patch('app.services.openf1.fetch_live_racecontrol')
    def test_websocket_connection_with_session_key(
        self,
        mock_race_control,
        mock_intervals,
        mock_positions
    ):
        """Test WebSocket connection to specific session"""
        # Setup mocks
        mock_positions.return_value = MOCK_POSITIONS
        mock_intervals.return_value = MOCK_INTERVALS
        mock_race_control.return_value = MOCK_RACE_CONTROL

        with client.websocket_connect("/ws/live/9158") as websocket:
            # Receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["session_key"] == "9158"
            assert "message" in data

            # Wait briefly for first update (polling interval is 4 seconds)
            # In test environment, we'll just verify connection works
            # Full polling test is done separately

    def test_websocket_accepts_pong_json_message(self):
        """Test WebSocket accepts JSON pong messages from client"""
        with client.websocket_connect("/ws/live/9158") as websocket:
            # Receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connected"
            
            # Send pong message as JSON
            websocket.send_json({"type": "pong"})
            
            # Connection should remain open (no error)
            # If we can send another message, connection is still alive
            websocket.send_json({"type": "pong"})

    @patch('app.routers.ws.fetch_current_session')
    def test_websocket_auto_session_no_session(self, mock_current_session):
        """Test auto session endpoint when no session is available"""
        mock_current_session.return_value = None

        with client.websocket_connect("/ws/live") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "No current session" in data["message"]

    @patch('app.routers.ws.determine_session_mode')
    @patch('app.routers.ws.fetch_current_session')
    def test_websocket_auto_session_not_live(
        self,
        mock_current_session,
        mock_mode
    ):
        """Test auto session endpoint when session is not live"""
        mock_current_session.return_value = MOCK_SESSION
        mock_mode.return_value = "upcoming"

        with client.websocket_connect("/ws/live") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert data["mode"] == "upcoming"
            assert "not live" in data["message"]

    @patch('app.routers.ws.fetch_current_session')
    @patch('app.routers.ws.determine_session_mode')
    @patch('app.ws.manager.fetch_live_positions')
    @patch('app.ws.manager.fetch_live_intervals')
    @patch('app.ws.manager.fetch_live_racecontrol')
    def test_websocket_auto_session_live(
        self,
        mock_race_control,
        mock_intervals,
        mock_positions,
        mock_mode,
        mock_current_session
    ):
        """Test auto session endpoint when session is live"""
        mock_current_session.return_value = MOCK_SESSION
        mock_mode.return_value = "live"
        mock_positions.return_value = MOCK_POSITIONS
        mock_intervals.return_value = MOCK_INTERVALS
        mock_race_control.return_value = MOCK_RACE_CONTROL

        with client.websocket_connect("/ws/live") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["session_key"] == "9158"
            assert data["mode"] == "live"
            assert "session_info" in data


class TestConnectionManager:
    """Test ConnectionManager functionality"""

    @pytest.mark.asyncio
    async def test_connection_manager_connect_disconnect(self):
        """Test ConnectionManager connect and disconnect methods"""
        manager = ConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        session_key = "test_session"

        # Test connect
        await manager.connect(mock_ws, session_key)
        assert session_key in manager.connections
        assert mock_ws in manager.connections[session_key]
        assert session_key in manager.tasks
        assert mock_ws in manager.heartbeat_tasks

        # Test disconnect
        await manager.disconnect(mock_ws, session_key)
        assert session_key not in manager.connections
        assert session_key not in manager.tasks
        assert mock_ws not in manager.heartbeat_tasks

    @pytest.mark.asyncio
    async def test_connection_manager_multiple_clients(self):
        """Test ConnectionManager with multiple clients on same session"""
        manager = ConnectionManager()
        mock_ws1 = MagicMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = MagicMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        session_key = "test_session"

        # Connect first client
        await manager.connect(mock_ws1, session_key)
        assert len(manager.connections[session_key]) == 1
        task1 = manager.tasks[session_key]

        # Connect second client
        await manager.connect(mock_ws2, session_key)
        assert len(manager.connections[session_key]) == 2
        # Should reuse same polling task
        assert manager.tasks[session_key] == task1

        # Disconnect first client
        await manager.disconnect(mock_ws1, session_key)
        assert len(manager.connections[session_key]) == 1
        # Polling should still be active
        assert session_key in manager.tasks

        # Disconnect second client
        await manager.disconnect(mock_ws2, session_key)
        # Polling should stop when no clients remain
        assert session_key not in manager.connections
        assert session_key not in manager.tasks

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast(self):
        """Test ConnectionManager broadcast method"""
        manager = ConnectionManager()
        mock_ws1 = MagicMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = MagicMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        session_key = "test_session"

        # Connect clients
        await manager.connect(mock_ws1, session_key)
        await manager.connect(mock_ws2, session_key)

        # Broadcast message
        test_data = {"type": "test", "message": "hello"}
        await manager.broadcast(session_key, test_data)

        # Verify both clients received the message
        mock_ws1.send_json.assert_called_with(test_data)
        mock_ws2.send_json.assert_called_with(test_data)

    @pytest.mark.asyncio
    async def test_connection_manager_broadcast_handles_dead_connections(self):
        """Test that broadcast removes dead connections"""
        manager = ConnectionManager()
        mock_ws_good = MagicMock()
        mock_ws_good.accept = AsyncMock()
        mock_ws_good.send_json = AsyncMock()

        mock_ws_dead = MagicMock()
        mock_ws_dead.accept = AsyncMock()
        mock_ws_dead.send_json = AsyncMock(side_effect=Exception("Connection closed"))

        session_key = "test_session"

        # Connect clients
        await manager.connect(mock_ws_good, session_key)
        await manager.connect(mock_ws_dead, session_key)

        assert len(manager.connections[session_key]) == 2

        # Broadcast message
        test_data = {"type": "test", "message": "hello"}
        await manager.broadcast(session_key, test_data)

        # Dead connection should be removed
        assert len(manager.connections[session_key]) == 1
        assert mock_ws_good in manager.connections[session_key]
        assert mock_ws_dead not in manager.connections[session_key]

    @pytest.mark.asyncio
    @patch('app.ws.manager.fetch_live_positions')
    @patch('app.ws.manager.fetch_live_intervals')
    @patch('app.ws.manager.fetch_live_racecontrol')
    async def test_polling_mechanism(
        self,
        mock_race_control,
        mock_intervals,
        mock_positions
    ):
        """Test that polling fetches data and broadcasts updates"""
        # Setup mocks as AsyncMock
        mock_positions.return_value = MOCK_POSITIONS
        mock_intervals.return_value = MOCK_INTERVALS
        mock_race_control.return_value = MOCK_RACE_CONTROL

        manager = ConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        session_key = "test_session"

        # Connect client (starts polling)
        await manager.connect(mock_ws, session_key)

        # Wait for at least one poll cycle (4 seconds + buffer)
        await asyncio.sleep(4.5)

        # Verify polling called the OpenF1 functions
        assert mock_positions.called
        assert mock_intervals.called
        assert mock_race_control.called

        # Verify broadcast was called with update data
        # Check if send_json was called with an update message
        calls = mock_ws.send_json.call_args_list
        update_calls = [call for call in calls if call[0][0].get("type") == "update"]
        assert len(update_calls) > 0

        # Verify update structure
        update_data = update_calls[0][0][0]
        assert update_data["type"] == "update"
        assert "timestamp" in update_data
        assert "positions" in update_data
        assert "intervals" in update_data
        assert "race_control" in update_data

        # Cleanup
        await manager.disconnect(mock_ws, session_key)

    @pytest.mark.asyncio
    async def test_heartbeat_mechanism(self):
        """Test that heartbeat sends periodic pings"""
        manager = ConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        session_key = "test_session"

        # Connect client (starts heartbeat)
        await manager.connect(mock_ws, session_key)

        # Wait for heartbeat interval (30 seconds is too long for test)
        # We'll just verify the heartbeat task was created
        assert mock_ws in manager.heartbeat_tasks
        assert not manager.heartbeat_tasks[mock_ws].done()

        # Cleanup
        await manager.disconnect(mock_ws, session_key)

        # Verify heartbeat task was cancelled
        assert mock_ws not in manager.heartbeat_tasks

    @pytest.mark.asyncio
    async def test_heartbeat_sends_ping_messages(self):
        """Test that heartbeat actually sends ping messages periodically"""
        manager = ConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        session_key = "test_session"

        # Connect client (starts heartbeat)
        await manager.connect(mock_ws, session_key)

        # Wait slightly longer than heartbeat interval to ensure ping is sent
        # Heartbeat interval is 30 seconds, but we'll wait 31 seconds
        await asyncio.sleep(31)

        # Verify ping was sent
        ping_calls = [call for call in mock_ws.send_json.call_args_list 
                      if call[0][0].get("type") == "ping"]
        assert len(ping_calls) >= 1, "Expected at least one ping message"

        # Cleanup
        await manager.disconnect(mock_ws, session_key)


    @pytest.mark.asyncio
    async def test_polling_lifecycle_with_multiple_clients(self):
        """Test that polling starts with first client and stops with last client"""
        manager = ConnectionManager()
        mock_ws1 = MagicMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = MagicMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        session_key = "test_session"

        # Initially no polling task
        assert session_key not in manager.tasks

        # Connect first client - polling should start
        await manager.connect(mock_ws1, session_key)
        assert session_key in manager.tasks
        assert not manager.tasks[session_key].done()
        polling_task_1 = manager.tasks[session_key]

        # Connect second client - same polling task should be reused
        await manager.connect(mock_ws2, session_key)
        assert session_key in manager.tasks
        assert manager.tasks[session_key] == polling_task_1  # Same task

        # Disconnect first client - polling should continue
        await manager.disconnect(mock_ws1, session_key)
        assert session_key in manager.tasks
        assert not manager.tasks[session_key].done()

        # Disconnect second client - polling should stop
        await manager.disconnect(mock_ws2, session_key)
        assert session_key not in manager.tasks
        assert session_key not in manager.connections

    @pytest.mark.asyncio
    @patch('app.ws.manager.fetch_live_positions')
    @patch('app.ws.manager.fetch_live_intervals')
    @patch('app.ws.manager.fetch_live_racecontrol')
    async def test_multiple_clients_receive_same_updates(
        self,
        mock_race_control,
        mock_intervals,
        mock_positions
    ):
        """Test that all connected clients receive the same broadcast updates"""
        # Setup mocks
        mock_positions.return_value = MOCK_POSITIONS
        mock_intervals.return_value = MOCK_INTERVALS
        mock_race_control.return_value = MOCK_RACE_CONTROL

        manager = ConnectionManager()
        mock_ws1 = MagicMock()
        mock_ws1.accept = AsyncMock()
        mock_ws1.send_json = AsyncMock()

        mock_ws2 = MagicMock()
        mock_ws2.accept = AsyncMock()
        mock_ws2.send_json = AsyncMock()

        mock_ws3 = MagicMock()
        mock_ws3.accept = AsyncMock()
        mock_ws3.send_json = AsyncMock()

        session_key = "test_session"

        # Connect three clients
        await manager.connect(mock_ws1, session_key)
        await manager.connect(mock_ws2, session_key)
        await manager.connect(mock_ws3, session_key)

        # Wait for at least one poll cycle
        await asyncio.sleep(4.5)

        # Verify all three clients received update messages
        for mock_ws in [mock_ws1, mock_ws2, mock_ws3]:
            calls = mock_ws.send_json.call_args_list
            update_calls = [call for call in calls if call[0][0].get("type") == "update"]
            assert len(update_calls) > 0, f"Client should have received at least one update"

            # Verify update structure
            update_data = update_calls[0][0][0]
            assert update_data["type"] == "update"
            assert "timestamp" in update_data
            assert "positions" in update_data
            assert "intervals" in update_data
            assert "race_control" in update_data

        # Verify all clients received the same data (compare first update from each)
        update1 = [call for call in mock_ws1.send_json.call_args_list if call[0][0].get("type") == "update"][0][0][0]
        update2 = [call for call in mock_ws2.send_json.call_args_list if call[0][0].get("type") == "update"][0][0][0]
        update3 = [call for call in mock_ws3.send_json.call_args_list if call[0][0].get("type") == "update"][0][0][0]

        # All updates should have the same positions, intervals, and race_control data
        assert update1["positions"] == update2["positions"] == update3["positions"]
        assert update1["intervals"] == update2["intervals"] == update3["intervals"]
        assert update1["race_control"] == update2["race_control"] == update3["race_control"]

        # Cleanup
        await manager.disconnect(mock_ws1, session_key)
        await manager.disconnect(mock_ws2, session_key)
        await manager.disconnect(mock_ws3, session_key)


class TestWebSocketErrorHandling:
    """Test WebSocket error handling"""

    @patch('app.ws.manager.fetch_live_positions')
    @patch('app.ws.manager.fetch_live_intervals')
    @patch('app.ws.manager.fetch_live_racecontrol')
    @pytest.mark.asyncio
    async def test_polling_handles_api_errors(
        self,
        mock_race_control,
        mock_intervals,
        mock_positions
    ):
        """Test that polling continues even if API calls fail"""
        # Setup mocks to raise exceptions
        mock_positions.side_effect = Exception("API Error")
        mock_intervals.return_value = MOCK_INTERVALS
        mock_race_control.return_value = MOCK_RACE_CONTROL

        manager = ConnectionManager()
        mock_ws = MagicMock()
        mock_ws.accept = AsyncMock()
        mock_ws.send_json = AsyncMock()

        session_key = "test_session"

        # Connect client
        await manager.connect(mock_ws, session_key)

        # Wait for poll cycle
        await asyncio.sleep(4.5)

        # Verify broadcast still happened with empty positions
        calls = mock_ws.send_json.call_args_list
        update_calls = [call for call in calls if call[0][0].get("type") == "update"]
        assert len(update_calls) > 0

        update_data = update_calls[0][0][0]
        assert update_data["positions"] == []  # Failed fetch returns empty list
        assert len(update_data["intervals"]) > 0  # Successful fetch returns data

        # Cleanup
        await manager.disconnect(mock_ws, session_key)
