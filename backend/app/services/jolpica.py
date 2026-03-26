"""
Jolpica F1 API Service

This module provides async functions for fetching historical F1 data from the Jolpica API
(community-maintained Ergast replacement). All functions use httpx.AsyncClient with
connection pooling for optimal performance.

API Documentation: https://ergast.com/mrd/
Base URL: https://api.jolpi.ca/ergast/f1
"""

import asyncio
import logging
from typing import Optional
import uuid

from app.cache.redis import redis_cache
from contextlib import asynccontextmanager

import httpx

logger = logging.getLogger(__name__)

# API Configuration
JOLPICA_API_BASE_URL = "https://api.jolpi.ca/ergast/f1"
REQUEST_TIMEOUT = 10.0  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds

# Shared httpx client for connection pooling
_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def get_client():
    """
    Context manager for httpx.AsyncClient with connection pooling.
    Reuses a single client instance across requests for optimal performance.
    """
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(REQUEST_TIMEOUT),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        )
    try:
        yield _client
    except Exception as e:
        logger.error(f"Error with httpx client: {e}")
        raise


async def close_client():
    """Close the shared httpx client. Should be called on application shutdown."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def _fetch_with_retry(
    url: str,
    request_id: Optional[str] = None,
    max_retries: int = MAX_RETRIES
) -> Optional[dict]:
    """
    Fetch data from URL with retry logic and error handling.
    
    Args:
        url: The URL to fetch data from
        request_id: Optional request ID for distributed tracing
        max_retries: Maximum number of retry attempts
        
    Returns:
        JSON response as dictionary, or None if request fails
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    async with get_client() as client:
        for attempt in range(max_retries):
            try:
                logger.info(f"[{request_id}] Fetching URL: {url} (attempt {attempt + 1}/{max_retries})")
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"[{request_id}] Successfully fetched data from {url}")
                return data
                
            except httpx.TimeoutException:
                logger.warning(f"[{request_id}] Request timed out for {url} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.error(f"[{request_id}] Request timed out after {max_retries} attempts: {url}")
                    return None
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    # Server error - retry
                    logger.warning(f"[{request_id}] Server error {e.response.status_code} for {url} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                        continue
                    else:
                        logger.error(f"[{request_id}] Server error after {max_retries} attempts: {url}")
                        return None
                else:
                    # Client error (4xx) - don't retry
                    logger.error(f"[{request_id}] Client error {e.response.status_code} for {url}")
                    return None
                    
            except httpx.RequestError as e:
                logger.error(f"[{request_id}] Network error for {url}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    return None
                    
            except ValueError as e:
                # JSON decode error
                logger.error(f"[{request_id}] Invalid JSON response from {url}: {e}")
                return None
                
            except Exception as e:
                logger.error(f"[{request_id}] Unexpected error fetching {url}: {e}")
                return None
    
    return None


async def fetch_driver_standings(
    year: str = "current",
    round_num: Optional[int] = None,
    request_id: Optional[str] = None
) -> Optional[list[dict]]:
    """
    Fetch driver championship standings from Jolpica F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
        round_num: Optional round number (1-based) for standings after specific round
        request_id: Optional request ID for distributed tracing
        
    Returns:
        List of driver standings dictionaries, or None if request fails
        
    Example response structure:
        [
            {
                "position": "1",
                "points": "575",
                "wins": "19",
                "Driver": {...},
                "Constructors": [...]
            },
            ...
        ]
    """
    if round_num is not None:
        url = f"{JOLPICA_API_BASE_URL}/{year}/{round_num}/driverStandings.json"
    else:
        url = f"{JOLPICA_API_BASE_URL}/{year}/driverStandings.json"
    
    data = await _fetch_with_retry(url, request_id)
    
    if data and 'MRData' in data and 'StandingsTable' in data['MRData']:
        standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
        if standings_lists:
            return standings_lists[0].get('DriverStandings', [])
    
    return None


async def fetch_constructor_standings(
    year: str = "current",
    round_num: Optional[int] = None,
    request_id: Optional[str] = None
) -> Optional[list[dict]]:
    """
    Fetch constructor championship standings from Jolpica F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
        round_num: Optional round number (1-based) for standings after specific round
        request_id: Optional request ID for distributed tracing
        
    Returns:
        List of constructor standings dictionaries, or None if request fails
        
    Example response structure:
        [
            {
                "position": "1",
                "points": "860",
                "wins": "21",
                "Constructor": {...}
            },
            ...
        ]
    """
    if round_num is not None:
        url = f"{JOLPICA_API_BASE_URL}/{year}/{round_num}/constructorStandings.json"
    else:
        url = f"{JOLPICA_API_BASE_URL}/{year}/constructorStandings.json"
    
    data = await _fetch_with_retry(url, request_id)
    
    if data and 'MRData' in data and 'StandingsTable' in data['MRData']:
        standings_lists = data['MRData']['StandingsTable'].get('StandingsLists', [])
        if standings_lists:
            return standings_lists[0].get('ConstructorStandings', [])
    
    return None


async def fetch_race_schedule(
    year: str = "current",
    request_id: Optional[str] = None
) -> Optional[list[dict]]:
    """
    Fetch the full race schedule for a given season from Jolpica F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023") or "current" for current season
        request_id: Optional request ID for distributed tracing
        
    Returns:
        List of all scheduled races in the season, or None if request fails
        
    Example response structure:
        [
            {
                "season": "2024",
                "round": "1",
                "raceName": "Bahrain Grand Prix",
                "Circuit": {...},
                "date": "2024-03-02",
                "time": "15:00:00Z"
            },
            ...
        ]
    """
    url = f"{JOLPICA_API_BASE_URL}/{year}.json"
    data = await _fetch_with_retry(url, request_id)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races:
            return races
    
    return None


async def fetch_race_results(
    year: str,
    round_num: int,
    request_id: Optional[str] = None
) -> Optional[dict]:
    """
    Fetch race results for a specific race from Jolpica F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023")
        round_num: Round number (1-based)
        request_id: Optional request ID for distributed tracing
        
    Returns:
        Dictionary containing race results, or None if request fails
        
    Example response structure:
        {
            "season": "2024",
            "round": "1",
            "raceName": "Bahrain Grand Prix",
            "Circuit": {...},
            "date": "2024-03-02",
            "Results": [
                {
                    "position": "1",
                    "points": "25",
                    "Driver": {...},
                    "Constructor": {...},
                    "grid": "1",
                    "laps": "57",
                    "status": "Finished",
                    "Time": {...},
                    "FastestLap": {...}
                },
                ...
            ]
        }
    """
    url = f"{JOLPICA_API_BASE_URL}/{year}/{round_num}/results.json"
    data = await _fetch_with_retry(url, request_id)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races:
            return races[0]
    
    return None


async def fetch_qualifying_results(
    year: str,
    round_num: int,
    request_id: Optional[str] = None
) -> Optional[dict]:
    """
    Fetch qualifying results for a specific race from Jolpica F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023")
        round_num: Round number (1-based)
        request_id: Optional request ID for distributed tracing
        
    Returns:
        Dictionary containing qualifying results, or None if request fails
        
    Example response structure:
        {
            "season": "2024",
            "round": "1",
            "raceName": "Bahrain Grand Prix",
            "Circuit": {...},
            "date": "2024-03-01",
            "QualifyingResults": [
                {
                    "position": "1",
                    "Driver": {...},
                    "Constructor": {...},
                    "Q1": "1:29.123",
                    "Q2": "1:28.456",
                    "Q3": "1:27.789"
                },
                ...
            ]
        }
    """
    url = f"{JOLPICA_API_BASE_URL}/{year}/{round_num}/qualifying.json"
    data = await _fetch_with_retry(url, request_id)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races:
            return races[0]
    
    return None


async def fetch_lap_times(
    year: str,
    round_num: int,
    request_id: Optional[str] = None
) -> Optional[list[dict]]:
    """
    Fetch lap times for a specific race from Jolpica F1 API.
    
    Args:
        year: Season year (e.g., "2024", "2023")
        round_num: Round number (1-based)
        request_id: Optional request ID for distributed tracing
        
    Returns:
        List of lap time dictionaries for all drivers, or None if request fails
        
    Example response structure:
        [
            {
                "driverId": "max_verstappen",
                "lap": "1",
                "position": "1",
                "time": "1:32.123"
            },
            ...
        ]
        
    Note: The API returns lap data nested within Laps array. This function
    flattens the structure for easier consumption.
    """
    # Use high limit to get all laps (races can have 50-70 laps)
    url = f"{JOLPICA_API_BASE_URL}/{year}/{round_num}/laps.json?limit=2000"
    data = await _fetch_with_retry(url, request_id)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        if races and len(races) > 0:
            race = races[0]
            laps = race.get('Laps', [])
            
            # Flatten lap data structure
            all_lap_times = []
            for lap in laps:
                lap_number = lap.get('number')
                timings = lap.get('Timings', [])
                
                for timing in timings:
                    all_lap_times.append({
                        'driverId': timing.get('driverId'),
                        'lap': lap_number,
                        'position': timing.get('position'),
                        'time': timing.get('time')
                    })
            
            return all_lap_times if all_lap_times else None
    
    return None


@redis_cache(ttl=3600, namespace="jolpica")
async def fetch_driver_race_results(
    driver_id: str,
    year: str = "current",
    request_id: Optional[str] = None
) -> Optional[list[dict]]:
    """
    Fetch all race results for a specific driver in a season from Jolpica F1 API.
    
    Args:
        driver_id: Driver ID (e.g., "max_verstappen", "hamilton")
        year: Season year (e.g., "2024", "2023") or "current" for current season
        request_id: Optional request ID for distributed tracing
        
    Returns:
        List of race dictionaries with results for the specified driver, or None if request fails
        
    Example response structure:
        [
            {
                "season": "2024",
                "round": "1",
                "raceName": "Bahrain Grand Prix",
                "Circuit": {...},
                "date": "2024-03-02",
                "Results": [
                    {
                        "position": "1",
                        "points": "25",
                        "Driver": {...},
                        "Constructor": {...},
                        "grid": "1",
                        "laps": "57",
                        "status": "Finished"
                    }
                ]
            },
            ...
        ]
    """
    # Use high limit to get all races in a season (max ~25 races)
    url = f"{JOLPICA_API_BASE_URL}/{year}/drivers/{driver_id}/results.json?limit=100"
    data = await _fetch_with_retry(url, request_id)
    
    if data and 'MRData' in data and 'RaceTable' in data['MRData']:
        races = data['MRData']['RaceTable'].get('Races', [])
        return races if races else None
    
    return None
