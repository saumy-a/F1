"""
Races router for race schedule, results, qualifying, and lap times.
"""
from fastapi import APIRouter, HTTPException, Path, Request
from typing import List
import logging

from app.models.races import Race, RaceResult, QualifyingResult, LapTime
from app.services.jolpica import (
    fetch_race_schedule,
    fetch_race_results,
    fetch_qualifying_results,
    fetch_lap_times
)
from app.cache.redis import redis_cache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/races/{year}",
    response_model=List[Race],
    summary="Get race schedule",
    description="Fetch the complete race schedule for a specific season"
)
@redis_cache(ttl=3600, namespace="jolpica")
async def get_race_schedule(
    request: Request,
    year: str = Path(..., description="Season year (e.g., '2024', '2023') or 'current'")
):
    """
    Get the complete race schedule for a season.
    
    - **year**: Season year or "current" for current season
    
    Returns list of all races in the season with circuit and date information.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching race schedule for year={year}")
        
        schedule = await fetch_race_schedule(
            year=year,
            request_id=request_id
        )
        
        if schedule is None:
            logger.warning(f"[{request_id}] No race schedule found for year={year}")
            raise HTTPException(
                status_code=404,
                detail=f"No race schedule found for year {year}"
            )
        
        logger.info(f"[{request_id}] Successfully fetched {len(schedule)} races")
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching race schedule: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching race schedule"
        )


@router.get(
    "/races/{year}/{round}/results",
    response_model=RaceResult,
    summary="Get race results",
    description="Fetch race results for a specific race"
)
@redis_cache(ttl=3600, namespace="jolpica")
async def get_race_results(
    request: Request,
    year: str = Path(..., description="Season year (e.g., '2024', '2023')"),
    round: int = Path(..., description="Round number (1-based)", ge=1, le=30)
):
    """
    Get race results for a specific race.
    
    - **year**: Season year
    - **round**: Round number (1-based)
    
    Returns complete race results including finishing positions, points, and fastest laps.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching race results for year={year}, round={round}")
        
        results = await fetch_race_results(
            year=year,
            round_num=round,
            request_id=request_id
        )
        
        if results is None:
            logger.warning(f"[{request_id}] No race results found for year={year}, round={round}")
            raise HTTPException(
                status_code=404,
                detail=f"No race results found for year {year} round {round}"
            )
        
        logger.info(f"[{request_id}] Successfully fetched race results with {len(results.get('Results', []))} entries")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching race results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching race results"
        )


@router.get(
    "/races/{year}/{round}/qualifying",
    response_model=QualifyingResult,
    summary="Get qualifying results",
    description="Fetch qualifying results for a specific race"
)
@redis_cache(ttl=3600, namespace="jolpica")
async def get_qualifying_results(
    request: Request,
    year: str = Path(..., description="Season year (e.g., '2024', '2023')"),
    round: int = Path(..., description="Round number (1-based)", ge=1, le=30)
):
    """
    Get qualifying results for a specific race.
    
    - **year**: Season year
    - **round**: Round number (1-based)
    
    Returns qualifying results with Q1, Q2, and Q3 times for all drivers.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching qualifying results for year={year}, round={round}")
        
        results = await fetch_qualifying_results(
            year=year,
            round_num=round,
            request_id=request_id
        )
        
        if results is None:
            logger.warning(f"[{request_id}] No qualifying results found for year={year}, round={round}")
            raise HTTPException(
                status_code=404,
                detail=f"No qualifying results found for year {year} round {round}"
            )
        
        logger.info(f"[{request_id}] Successfully fetched qualifying results with {len(results.get('QualifyingResults', []))} entries")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching qualifying results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching qualifying results"
        )


@router.get(
    "/races/{year}/{round}/laps",
    response_model=List[LapTime],
    summary="Get lap times",
    description="Fetch all lap times for a specific race"
)
@redis_cache(ttl=3600, namespace="jolpica")
async def get_lap_times(
    request: Request,
    year: str = Path(..., description="Season year (e.g., '2024', '2023')"),
    round: int = Path(..., description="Round number (1-based)", ge=1, le=30)
):
    """
    Get all lap times for a specific race.
    
    - **year**: Season year
    - **round**: Round number (1-based)
    
    Returns lap times for all drivers across all laps of the race.
    Note: This can be a large dataset (50-70 laps × 20 drivers = 1000-1400 entries).
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching lap times for year={year}, round={round}")
        
        lap_times = await fetch_lap_times(
            year=year,
            round_num=round,
            request_id=request_id
        )
        
        if lap_times is None:
            logger.warning(f"[{request_id}] No lap times found for year={year}, round={round}")
            raise HTTPException(
                status_code=404,
                detail=f"No lap times found for year {year} round {round}"
            )
        
        logger.info(f"[{request_id}] Successfully fetched {len(lap_times)} lap times")
        return lap_times
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching lap times: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching lap times"
        )
