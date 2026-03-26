"""
WebSocket ConnectionManager for real-time F1 race data streaming.

This module manages WebSocket connections and broadcasts live race updates
by polling the OpenF1 API at regular intervals.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import WebSocket

from app.services.openf1 import (
    fetch_live_positions,
    fetch_live_intervals,
    fetch_live_racecontrol,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts live race data"""

    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
        self.heartbeat_tasks: Dict[WebSocket, asyncio.Task] = {}

    async def connect(self, ws: WebSocket, session_key: str):
        """Accept new WebSocket connection and start polling if needed"""
        await ws.accept()
        self.connections.setdefault(session_key, []).append(ws)
        logger.info(
            f"Client connected to session {session_key} "
            f"(total: {len(self.connections[session_key])})"
        )

        # Start heartbeat for this connection
        self.heartbeat_tasks[ws] = asyncio.create_task(self._heartbeat(ws))

        # Start polling task if this is first client for session
        if session_key not in self.tasks:
            self.tasks[session_key] = asyncio.create_task(self._poll(session_key))
            logger.info(f"Started polling for session {session_key}")

    async def disconnect(self, ws: WebSocket, session_key: str):
        """Remove WebSocket connection and stop polling if no clients remain"""
        if session_key in self.connections:
            if ws in self.connections[session_key]:
                self.connections[session_key].remove(ws)
                logger.info(
                    f"Client disconnected from session {session_key} "
                    f"(remaining: {len(self.connections[session_key])})"
                )

            # Cancel heartbeat
            if ws in self.heartbeat_tasks:
                self.heartbeat_tasks[ws].cancel()
                del self.heartbeat_tasks[ws]

            # Stop polling if no more clients
            if not self.connections[session_key]:
                if session_key in self.tasks:
                    self.tasks[session_key].cancel()
                    del self.tasks[session_key]
                del self.connections[session_key]
                logger.info(f"Stopped polling for session {session_key}")

    async def broadcast(self, session_key: str, data: dict):
        """Broadcast data to all clients connected to session"""
        dead = []
        for ws in self.connections.get(session_key, []):
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                dead.append(ws)

        # Clean up dead connections
        for ws in dead:
            await self.disconnect(ws, session_key)

    async def _poll(self, session_key: str):
        """Poll OpenF1 API and broadcast updates every 4 seconds"""
        while True:
            try:
                # Fetch all live data in parallel
                positions, intervals, race_control = await asyncio.gather(
                    fetch_live_positions(session_key),
                    fetch_live_intervals(session_key),
                    fetch_live_racecontrol(session_key),
                    return_exceptions=True,
                )

                # Broadcast update
                await self.broadcast(
                    session_key,
                    {
                        "type": "update",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "positions": (
                            positions if not isinstance(positions, Exception) else []
                        ),
                        "intervals": (
                            intervals if not isinstance(intervals, Exception) else []
                        ),
                        "race_control": (
                            race_control
                            if not isinstance(race_control, Exception)
                            else []
                        ),
                    },
                )

            except asyncio.CancelledError:
                logger.info(f"Polling cancelled for session {session_key}")
                break
            except Exception as e:
                logger.error(f"Poll error for {session_key}: {e}")

            await asyncio.sleep(4)

    async def _heartbeat(self, ws: WebSocket):
        """Send periodic ping to detect stale connections"""
        try:
            while True:
                await asyncio.sleep(30)
                await ws.send_json({"type": "ping"})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")


# Global instance
manager = ConnectionManager()
