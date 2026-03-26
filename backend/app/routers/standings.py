"""
Standings router for driver and constructor championship standings.
"""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional
import logging

from app.models.standings import DriverStanding, ConstructorStanding
from app.services.jolpica import fetch_driver_standings, fetch_constructor_standings
from app.cache.redis import redis_cache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/standings/drivers/{year}",
    response_model=List[DriverStanding],
    summary="Get driver championship standings",
    description="Fetch driver championship standings for a specific year and optional round"
)
@redis_cache(ttl=3600, namespace="jolpica")
async def get_driver_standings(
    request: Request,
    year: str,
    round: Optional[int] = Query(None, description="Round number (1-based). If not provided, returns final standings")
):
    """
    Get driver championship standings for a specific year.
    
    - **year**: Season year (e.g., "2024", "2023") or "current" for current season
    - **round**: Optional round number to get standings after that round
    
    Returns list of driver standings sorted by position.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching driver standings for year={year}, round={round}")
        
        standings = await fetch_driver_standings(
            year=year,
            round_num=round,
            request_id=request_id
        )
        
        if standings is None:
            logger.warning(f"[{request_id}] No driver standings found for year={year}, round={round}")
            raise HTTPException(
                status_code=404,
                detail=f"No driver standings found for year {year}" + (f" round {round}" if round else "")
            )
        
        logger.info(f"[{request_id}] Successfully fetched {len(standings)} driver standings")
        return standings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching driver standings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching driver standings"
        )


@router.get(
    "/standings/constructors/{year}",
    response_model=List[ConstructorStanding],
    summary="Get constructor championship standings",
    description="Fetch constructor championship standings for a specific year and optional round"
)
@redis_cache(ttl=3600, namespace="jolpica")
async def get_constructor_standings(
    request: Request,
    year: str,
    round: Optional[int] = Query(None, description="Round number (1-based). If not provided, returns final standings")
):
    """
    Get constructor championship standings for a specific year.
    
    - **year**: Season year (e.g., "2024", "2023") or "current" for current season
    - **round**: Optional round number to get standings after that round
    
    Returns list of constructor standings sorted by position.
    """
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching constructor standings for year={year}, round={round}")
        
        standings = await fetch_constructor_standings(
            year=year,
            round_num=round,
            request_id=request_id
        )
        
        if standings is None:
            logger.warning(f"[{request_id}] No constructor standings found for year={year}, round={round}")
            raise HTTPException(
                status_code=404,
                detail=f"No constructor standings found for year {year}" + (f" round {round}" if round else "")
            )
        
        logger.info(f"[{request_id}] Successfully fetched {len(standings)} constructor standings")
        return standings
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching constructor standings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching constructor standings"
        )
