"""
OpenF1 API Service

This module provides async functions for fetching real-time F1 data from the OpenF1 API.
OpenF1 provides live telemetry data for races from 2023 onwards.

API Documentation: https://openf1.org/
Base URL: https://api.openf1.org/v1
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

OPENF1_BASE_URL = "https://api.openf1.org/v1"
REQUEST_TIMEOUT = 10.0

# Shared HTTP client with connection pooling
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """
    Get or create a shared HTTP client with connection pooling.
    
    Returns:
        Configured AsyncClient with connection pooling
    """
    global _http_client
    
    # Check if client exists and is not closed
    if _http_client is not None and not _http_client.is_closed:
        return _http_client
    
    # Create new client
    _http_client = httpx.AsyncClient(
        timeout=REQUEST_TIMEOUT,
        limits=httpx.Limits(max_keepalive_connections=20)
    )
    return _http_client


async def close_http_client():
    """Close the shared HTTP client."""
    global _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()
    _http_client = None


async def fetch_current_session(
    request_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch current or most recent F1 session information.
    
    Returns:
        Dict with session info including session_key, session_name, date_start, etc.
        None if no session found or request fails
    """
    url = f"{OPENF1_BASE_URL}/sessions?session_key=latest"
    
    try:
        client = get_http_client()
        logger.info(f"[{request_id}] Fetching current session from OpenF1")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            logger.info(f"[{request_id}] Successfully fetched session: {data[0].get('session_name', 'unknown')}")
            return data[0]
        
        logger.warning(f"[{request_id}] No current session found")
        return None
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching session: {e}")
        return None
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching session: {e}")
        return None


async def fetch_session_by_key(
    session_key: str,
    request_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch a specific session by its session_key.
    
    Args:
        session_key: Session identifier
        
    Returns:
        Dict with session info including session_key, session_name, date_start, etc.
        None if no session found or request fails
    """
    url = f"{OPENF1_BASE_URL}/sessions?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.info(f"[{request_id}] Fetching session {session_key} from OpenF1")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            logger.info(f"[{request_id}] Successfully fetched session: {data[0].get('session_name', 'unknown')}")
            return data[0]
        
        logger.warning(f"[{request_id}] Session {session_key} not found")
        return None
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching session {session_key}: {e}")
        return None
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching session {session_key}: {e}")
        return None


async def fetch_session_drivers(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch list of drivers participating in a session.
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of driver dicts with driver_number, name_acronym, team_name, etc.
    """
    url = f"{OPENF1_BASE_URL}/drivers?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.info(f"[{request_id}] Fetching drivers for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"[{request_id}] Successfully fetched {len(data)} drivers")
        return data
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching drivers: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching drivers: {e}")
        return []


async def fetch_live_positions(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch current race positions for all drivers.
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of position dicts with driver_number, position, date
    """
    url = f"{OPENF1_BASE_URL}/position?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.debug(f"[{request_id}] Fetching live positions for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        # Get most recent position for each driver
        if data:
            # Group by driver_number and get latest
            latest_positions = {}
            for pos in data:
                driver_num = pos.get('driver_number')
                if driver_num:
                    latest_positions[driver_num] = pos
            
            result = list(latest_positions.values())
            logger.debug(f"[{request_id}] Fetched {len(result)} live positions")
            return result
        
        return []
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching positions: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching positions: {e}")
        return []


async def fetch_live_intervals(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch time intervals between drivers.
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of interval dicts with driver_number, gap_to_leader, interval
    """
    url = f"{OPENF1_BASE_URL}/intervals?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.debug(f"[{request_id}] Fetching live intervals for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        # Get most recent interval for each driver
        if data:
            latest_intervals = {}
            for interval in data:
                driver_num = interval.get('driver_number')
                if driver_num:
                    latest_intervals[driver_num] = interval
            
            result = list(latest_intervals.values())
            logger.debug(f"[{request_id}] Fetched {len(result)} live intervals")
            return result
        
        return []
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching intervals: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching intervals: {e}")
        return []


async def fetch_live_stints(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch tire stint information for all drivers.
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of stint dicts with driver_number, stint_number, compound, tyre_age_at_start
    """
    url = f"{OPENF1_BASE_URL}/stints?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.debug(f"[{request_id}] Fetching stints for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"[{request_id}] Fetched {len(data)} stints")
        return data
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching stints: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching stints: {e}")
        return []


async def fetch_live_pits(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch pit stop data for the session.
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of pit stop dicts with driver_number, lap_number, pit_duration
    """
    url = f"{OPENF1_BASE_URL}/pit?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.debug(f"[{request_id}] Fetching pit stops for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"[{request_id}] Fetched {len(data)} pit stops")
        return data
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching pits: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching pits: {e}")
        return []


async def fetch_live_weather(
    session_key: str,
    request_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch current weather conditions at the circuit.
    
    Args:
        session_key: Session identifier
        
    Returns:
        Dict with weather data (air_temperature, track_temperature, humidity, etc.)
        None if no data available
    """
    url = f"{OPENF1_BASE_URL}/weather?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.debug(f"[{request_id}] Fetching weather for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            # Return most recent weather data
            logger.debug(f"[{request_id}] Fetched weather data")
            return data[-1]
        
        return None
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching weather: {e}")
        return None
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching weather: {e}")
        return None


async def fetch_live_racecontrol(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch race control messages (flags, penalties, safety car, etc.).
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of race control message dicts
    """
    url = f"{OPENF1_BASE_URL}/race_control?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.debug(f"[{request_id}] Fetching race control messages for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"[{request_id}] Fetched {len(data)} race control messages")
        return data
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching race control: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching race control: {e}")
        return []



async def fetch_live_radio(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch team radio communications for the session.
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of team radio dicts with driver_number, date, recording_url, duration
    """
    url = f"{OPENF1_BASE_URL}/team_radio?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.debug(f"[{request_id}] Fetching team radio for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        logger.debug(f"[{request_id}] Fetched {len(data)} team radio clips")
        return data
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching team radio: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching team radio: {e}")
        return []


async def fetch_sessions_by_year(
    year: int,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch all F1 sessions for a given year.
    
    Args:
        year: Year to fetch sessions for (e.g., 2024)
        
    Returns:
        List of session dicts with session_key, session_name, date_start, etc.
    """
    url = f"{OPENF1_BASE_URL}/sessions?year={year}"
    
    try:
        client = get_http_client()
        logger.info(f"[{request_id}] Fetching sessions for year {year}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"[{request_id}] Successfully fetched {len(data)} sessions for {year}")
        return data
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching sessions: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching sessions: {e}")
        return []


async def fetch_starting_grid(
    session_key: str,
    request_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch starting grid positions for a session.
    
    This fetches the initial positions at the start of the session,
    which represents the starting grid for a race or qualifying order.
    
    Args:
        session_key: Session identifier
        
    Returns:
        List of position dicts with driver_number, position, representing starting grid
    """
    url = f"{OPENF1_BASE_URL}/position?session_key={session_key}"
    
    try:
        client = get_http_client()
        logger.info(f"[{request_id}] Fetching starting grid for session {session_key}")
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        if not data:
            logger.warning(f"[{request_id}] No position data found for session {session_key}")
            return []
        
        # Get the earliest position data for each driver (starting grid)
        # Group by driver_number and get the earliest timestamp
        from collections import defaultdict
        driver_positions = defaultdict(list)
        
        for pos in data:
            driver_num = pos.get('driver_number')
            if driver_num:
                driver_positions[driver_num].append(pos)
        
        # For each driver, get the earliest position (starting grid)
        starting_grid = []
        for driver_num, positions in driver_positions.items():
            # Sort by date and take the first one
            earliest = min(positions, key=lambda p: p.get('date', ''))
            starting_grid.append(earliest)
        
        # Sort by position
        starting_grid.sort(key=lambda p: p.get('position', 999))
        
        logger.info(f"[{request_id}] Successfully fetched starting grid with {len(starting_grid)} positions")
        return starting_grid
        
    except httpx.HTTPError as e:
        logger.error(f"[{request_id}] OpenF1 API error fetching starting grid: {e}")
        return []
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error fetching starting grid: {e}")
        return []
