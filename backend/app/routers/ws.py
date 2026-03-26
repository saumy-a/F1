"""
WebSocket router for real-time F1 race data streaming.

This module provides WebSocket endpoints for clients to receive live race updates
including positions, intervals, and race control messages.
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.ws.manager import manager
from app.services.openf1 import fetch_current_session
from app.services.live import determine_session_mode

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/live/{session_key}")
async def websocket_live_race(websocket: WebSocket, session_key: str):
    """
    WebSocket endpoint for live race updates for a specific session.
    
    Args:
        websocket: WebSocket connection
        session_key: OpenF1 session key (e.g., "9158")
        
    The endpoint:
    - Validates session_key parameter (must be numeric string)
    - Accepts the WebSocket connection
    - Starts polling OpenF1 API every 4 seconds
    - Broadcasts position, interval, and race control updates
    - Listens for pong messages from client
    - Handles disconnections gracefully
    """
    # Validate session_key parameter (must be numeric string)
    if not session_key.isdigit():
        await websocket.close(code=1008, reason="Invalid session_key: must be numeric string")
        logger.warning(f"Rejected WebSocket connection: invalid session_key '{session_key}'")
        return
    
    await manager.connect(websocket, session_key)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_key": session_key,
            "message": f"Connected to session {session_key}"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Receive messages from client (e.g., pong responses)
            data = await websocket.receive_text()
            
            # Parse JSON message
            try:
                message = json.loads(data)
                
                # Handle pong responses to ping
                if message.get("type") == "pong":
                    logger.debug(f"Received pong from client for session {session_key}")
            except json.JSONDecodeError:
                logger.warning(f"Received non-JSON message from client: {data}")
            
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from session {session_key}")
        await manager.disconnect(websocket, session_key)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_key}: {e}")
        await manager.disconnect(websocket, session_key)


@router.websocket("/live")
async def websocket_auto_session(websocket: WebSocket):
    """
    WebSocket endpoint that automatically connects to the current live session.
    
    Args:
        websocket: WebSocket connection
        
    The endpoint:
    - Fetches the current session from OpenF1 API
    - Determines if the session is live, upcoming, or replay
    - Connects to the appropriate session if live
    - Rejects connection if no live session is available
    """
    try:
        # Fetch current session
        session_info = await fetch_current_session()
        
        if not session_info:
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "message": "No current session available"
            })
            await websocket.close()
            return
        
        # Determine session mode
        mode = determine_session_mode(session_info)
        session_key = str(session_info.get('session_key', ''))
        
        if mode != "live":
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "mode": mode,
                "message": f"Session is {mode}, not live",
                "session_info": session_info
            })
            await websocket.close()
            return
        
        # Connect to live session
        await manager.connect(websocket, session_key)
        
        try:
            # Send initial connection confirmation with session info
            await websocket.send_json({
                "type": "connected",
                "session_key": session_key,
                "mode": mode,
                "session_info": session_info,
                "message": f"Connected to live session {session_key}"
            })
            
            # Keep connection alive and handle incoming messages
            while True:
                data = await websocket.receive_text()
                
                # Parse JSON message
                try:
                    message = json.loads(data)
                    
                    # Handle pong responses to ping
                    if message.get("type") == "pong":
                        logger.debug(f"Received pong from client on auto session {session_key}")
                except json.JSONDecodeError:
                    logger.warning(f"Received non-JSON message from client: {data}")
                
        except WebSocketDisconnect:
            logger.info(f"Client disconnected from auto session {session_key}")
            await manager.disconnect(websocket, session_key)
        except Exception as e:
            logger.error(f"WebSocket error for auto session {session_key}: {e}")
            await manager.disconnect(websocket, session_key)
            
    except Exception as e:
        logger.error(f"Error in auto session WebSocket: {e}")
        try:
            await websocket.accept()
            await websocket.send_json({
                "type": "error",
                "message": f"Failed to connect: {str(e)}"
            })
            await websocket.close()
        except:
            pass
