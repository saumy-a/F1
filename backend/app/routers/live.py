"""
Live data router for OpenF1 real-time race data.
"""
from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
import logging

from app.models.live import (
    SessionInfo,
    Driver,
    Position,
    Interval,
    Stint,
    PitStop,
    Weather,
    RaceControlMessage,
    TeamRadio,
    LiveDataAggregate
)
from app.services.openf1 import (
    fetch_current_session,
    fetch_session_by_key,
    fetch_session_drivers,
    fetch_live_positions,
    fetch_live_intervals,
    fetch_live_stints,
    fetch_live_pits,
    fetch_live_weather,
    fetch_live_racecontrol,
    fetch_live_radio,
    fetch_sessions_by_year,
    fetch_starting_grid
)
from app.services.live import determine_session_mode, aggregate_live_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/live/session",
    response_model=SessionInfo,
    summary="Get current session info",
    description="Fetch current or most recent F1 session information"
)
async def get_current_session(request: Request):
    """Get current session information with mode determination."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching current session")
        
        session = await fetch_current_session(request_id=request_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="No current session found")
        
        # Determine session mode
        mode = determine_session_mode(session)
        session['mode'] = mode
        
        logger.info(f"[{request_id}] Current session: {session.get('session_name')} ({mode})")
        return SessionInfo.model_validate(session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching current session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching session")


@router.get(
    "/live/session/{session_key}",
    response_model=SessionInfo,
    summary="Get session info by key",
    description="Fetch F1 session information for a specific session_key"
)
async def get_session_by_key(request: Request, session_key: str):
    """Get session information with mode determination."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching session {session_key}")
        
        session = await fetch_session_by_key(session_key, request_id=request_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Determine session mode
        mode = determine_session_mode(session)
        session['mode'] = mode
        
        logger.info(f"[{request_id}] Session {session_key}: {session.get('session_name')} ({mode})")
        return SessionInfo.model_validate(session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching session {session_key}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching session")


@router.get(
    "/live/drivers",
    response_model=List[Driver],
    summary="Get session drivers",
    description="Fetch list of drivers in the current session"
)
async def get_session_drivers(
    request: Request,
    session_key: Optional[str] = None
):
    """Get drivers participating in a session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        # If no session_key provided, get current session
        if not session_key:
            session = await fetch_current_session(request_id=request_id)
            if not session:
                raise HTTPException(status_code=404, detail="No current session found")
            session_key = session.get('session_key')
        
        logger.info(f"[{request_id}] Fetching drivers for session {session_key}")
        
        drivers = await fetch_session_drivers(session_key, request_id=request_id)
        
        logger.info(f"[{request_id}] Found {len(drivers)} drivers")
        return [Driver.model_validate(d) for d in drivers]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching drivers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching drivers")


@router.get(
    "/live/sessions",
    response_model=List[SessionInfo],
    summary="Get sessions by year",
    description="Fetch list of F1 sessions for a given year"
)
async def get_sessions_by_year(
    request: Request,
    year: int
):
    """Get list of sessions for a specific year."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching sessions for year {year}")
        
        sessions = await fetch_sessions_by_year(year, request_id=request_id)
        
        if not sessions:
            logger.warning(f"[{request_id}] No sessions found for year {year}")
            return []
        
        # Add mode to each session
        result = []
        for session in sessions:
            mode = determine_session_mode(session)
            session['mode'] = mode
            result.append(SessionInfo.model_validate(session))
        
        logger.info(f"[{request_id}] Found {len(result)} sessions for year {year}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching sessions")


@router.get(
    "/live/positions/{session_key}",
    response_model=List[Position],
    summary="Get live positions",
    description="Fetch current race positions for all drivers in a session"
)
async def get_live_positions(
    request: Request,
    session_key: str
):
    """Get current race positions for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.debug(f"[{request_id}] Fetching positions for session {session_key}")
        
        positions = await fetch_live_positions(session_key, request_id=request_id)
        
        if not positions:
            logger.warning(f"[{request_id}] No positions found for session {session_key}")
            return []
        
        return [Position.model_validate(p) for p in positions]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching positions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching positions")


@router.get(
    "/live/intervals/{session_key}",
    response_model=List[Interval],
    summary="Get live intervals",
    description="Fetch time intervals between drivers in a session"
)
async def get_live_intervals(
    request: Request,
    session_key: str
):
    """Get time intervals between drivers for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.debug(f"[{request_id}] Fetching intervals for session {session_key}")
        
        intervals = await fetch_live_intervals(session_key, request_id=request_id)
        
        if not intervals:
            logger.warning(f"[{request_id}] No intervals found for session {session_key}")
            return []
        
        return [Interval.model_validate(i) for i in intervals]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching intervals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching intervals")


@router.get(
    "/live/stints/{session_key}",
    response_model=List[Stint],
    summary="Get tire stints",
    description="Fetch tire stint information for all drivers in a session"
)
async def get_live_stints(
    request: Request,
    session_key: str
):
    """Get tire stint information for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.debug(f"[{request_id}] Fetching stints for session {session_key}")
        
        stints = await fetch_live_stints(session_key, request_id=request_id)
        
        if not stints:
            logger.warning(f"[{request_id}] No stints found for session {session_key}")
            return []
        
        return [Stint.model_validate(s) for s in stints]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching stints: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching stints")


@router.get(
    "/live/pits/{session_key}",
    response_model=List[PitStop],
    summary="Get pit stops",
    description="Fetch pit stop data for a session"
)
async def get_live_pits(
    request: Request,
    session_key: str
):
    """Get pit stop data for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.debug(f"[{request_id}] Fetching pit stops for session {session_key}")
        
        pits = await fetch_live_pits(session_key, request_id=request_id)
        
        if not pits:
            logger.warning(f"[{request_id}] No pit stops found for session {session_key}")
            return []
        
        return [PitStop.model_validate(p) for p in pits]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching pit stops: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching pit stops")


@router.get(
    "/live/weather/{session_key}",
    response_model=Weather,
    summary="Get weather conditions",
    description="Fetch current weather conditions at the circuit for a session"
)
async def get_live_weather(
    request: Request,
    session_key: str
):
    """Get current weather conditions for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.debug(f"[{request_id}] Fetching weather for session {session_key}")
        
        weather = await fetch_live_weather(session_key, request_id=request_id)
        
        if not weather:
            raise HTTPException(status_code=404, detail="No weather data available for this session")
        
        return Weather.model_validate(weather)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching weather: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching weather")


@router.get(
    "/live/race-control/{session_key}",
    response_model=List[RaceControlMessage],
    summary="Get race control messages",
    description="Fetch race control messages (flags, penalties, safety car, etc.) for a session"
)
async def get_race_control(
    request: Request,
    session_key: str
):
    """Get race control messages for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.debug(f"[{request_id}] Fetching race control messages for session {session_key}")
        
        messages = await fetch_live_racecontrol(session_key, request_id=request_id)
        
        if not messages:
            logger.warning(f"[{request_id}] No race control messages found for session {session_key}")
            return []
        
        return [RaceControlMessage.model_validate(m) for m in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching race control messages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching race control")


@router.get(
    "/live/radio/{session_key}",
    response_model=List[TeamRadio],
    summary="Get team radio",
    description="Fetch team radio communications for a session"
)
async def get_team_radio(
    request: Request,
    session_key: str
):
    """Get team radio communications for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.debug(f"[{request_id}] Fetching team radio for session {session_key}")
        
        radio = await fetch_live_radio(session_key, request_id=request_id)
        
        if not radio:
            logger.warning(f"[{request_id}] No team radio found for session {session_key}")
            return []
        
        return [TeamRadio.model_validate(r) for r in radio]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching team radio: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching team radio")


@router.get(
    "/live/grid/{session_key}",
    response_model=List[Position],
    summary="Get starting grid",
    description="Fetch starting grid positions for a session"
)
async def get_starting_grid(
    request: Request,
    session_key: str
):
    """Get starting grid positions for a specific session."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        logger.info(f"[{request_id}] Fetching starting grid for session {session_key}")
        
        grid = await fetch_starting_grid(session_key, request_id=request_id)
        
        if not grid:
            raise HTTPException(status_code=404, detail="No starting grid data available for this session")
        
        return [Position.model_validate(p) for p in grid]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching starting grid: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching starting grid")


@router.get(
    "/live/aggregate",
    response_model=LiveDataAggregate,
    summary="Get aggregated live data",
    description="Fetch all live data in a single request"
)
async def get_aggregated_live_data(
    request: Request,
    session_key: Optional[str] = None
):
    """Get all live data aggregated in one response."""
    request_id = getattr(request.state, 'request_id', None)
    
    try:
        if not session_key:
            session = await fetch_current_session(request_id=request_id)
            if not session:
                raise HTTPException(status_code=404, detail="No current session found")
            session_key = session.get('session_key')
        
        logger.info(f"[{request_id}] Fetching aggregated live data for session {session_key}")
        
        data = await aggregate_live_data(session_key, request_id=request_id)
        
        return LiveDataAggregate.model_validate(data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error fetching aggregated data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error while fetching aggregated data")
