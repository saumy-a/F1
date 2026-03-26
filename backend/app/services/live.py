"""
Live session mode determination and data aggregation.

This module handles the logic for determining whether a session is live, upcoming, or replay,
and aggregates data from multiple OpenF1 API calls.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.services.openf1 import (
    fetch_current_session,
    fetch_session_drivers,
    fetch_live_positions,
    fetch_live_intervals,
    fetch_live_stints,
    fetch_live_pits,
    fetch_live_weather,
    fetch_live_racecontrol
)

logger = logging.getLogger(__name__)


def determine_session_mode(session_info: Dict[str, Any]) -> str:
    """
    Determine if a session is live, upcoming, or replay based on timestamps.
    
    Args:
        session_info: Session dict from OpenF1 API with date_start and date_end
        
    Returns:
        "live" if session is currently active
        "upcoming" if session hasn't started yet
        "replay" if session has ended
    """
    try:
        # Get current UTC time
        now = datetime.now(timezone.utc)
        
        # Parse session start and end times
        date_start_str = session_info.get('date_start')
        date_end_str = session_info.get('date_end')
        
        if not date_start_str:
            logger.warning("Session missing date_start, defaulting to replay mode")
            return "replay"
        
        # Parse ISO format timestamps
        date_start = datetime.fromisoformat(date_start_str.replace('Z', '+00:00'))
        
        # If no end date, assume session is 2 hours long
        if date_end_str:
            date_end = datetime.fromisoformat(date_end_str.replace('Z', '+00:00'))
        else:
            from datetime import timedelta
            date_end = date_start + timedelta(hours=2)
        
        # Determine mode
        if now < date_start:
            return "upcoming"
        elif now > date_end:
            return "replay"
        else:
            return "live"
            
    except Exception as e:
        logger.error(f"Error determining session mode: {e}")
        return "replay"


async def aggregate_live_data(
    session_key: str,
    request_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Aggregate all live data from multiple OpenF1 API calls.
    
    Args:
        session_key: Session identifier
        request_id: Optional request ID for tracing
        
    Returns:
        Dict containing all live data:
        - drivers: List of drivers in session
        - positions: Current race positions
        - intervals: Time gaps between drivers
        - stints: Tire stint information
        - pits: Pit stop data
        - weather: Current weather conditions
        - race_control: Race control messages
    """
    try:
        logger.info(f"[{request_id}] Aggregating live data for session {session_key}")
        
        # Fetch all data in parallel for efficiency
        import asyncio
        drivers, positions, intervals, stints, pits, weather, race_control = await asyncio.gather(
            fetch_session_drivers(session_key, request_id),
            fetch_live_positions(session_key, request_id),
            fetch_live_intervals(session_key, request_id),
            fetch_live_stints(session_key, request_id),
            fetch_live_pits(session_key, request_id),
            fetch_live_weather(session_key, request_id),
            fetch_live_racecontrol(session_key, request_id),
            return_exceptions=True
        )
        
        # Handle any exceptions from parallel fetches
        def safe_result(result, default):
            return result if not isinstance(result, Exception) else default
        
        aggregated_data = {
            "session_key": session_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drivers": safe_result(drivers, []),
            "positions": safe_result(positions, []),
            "intervals": safe_result(intervals, []),
            "stints": safe_result(stints, []),
            "pits": safe_result(pits, []),
            "weather": safe_result(weather, None),
            "race_control": safe_result(race_control, [])
        }
        
        logger.info(f"[{request_id}] Successfully aggregated live data")
        return aggregated_data
        
    except Exception as e:
        logger.error(f"[{request_id}] Error aggregating live data: {e}")
        return {
            "session_key": session_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "drivers": [],
            "positions": [],
            "intervals": [],
            "stints": [],
            "pits": [],
            "weather": None,
            "race_control": [],
            "error": str(e)
        }
