---
title: Backend Patterns
inclusion: auto
---

# Backend Patterns for F1 Dashboard

## Request ID Middleware for Distributed Tracing

```python
# backend/app/middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request for distributed tracing.
    Request ID can be provided by client via X-Request-ID header or generated.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Get request ID from header or generate new one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Store in request state for access in route handlers
        request.state.request_id = request_id
        
        # Log incoming request with ID
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Log response with ID
        logger.info(
            f"Response {request_id}: {response.status_code}",
            extra={"request_id": request_id, "status_code": response.status_code}
        )
        
        return response

# backend/app/main.py
from app.middleware.request_id import RequestIDMiddleware

app = FastAPI(title="F1 Dashboard API", version="2.0", lifespan=lifespan)

# Add request ID middleware (should be first)
app.add_middleware(RequestIDMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Logging Configuration with Request ID

```python
# backend/app/config.py
import logging
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... other settings ...
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Configure logging with request ID support
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add default request_id for logs outside request context
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'system'
        return True

for handler in logging.root.handlers:
    handler.addFilter(RequestIDFilter())
```

## Using Request ID in Route Handlers

```python
# backend/app/routers/standings.py
from fastapi import APIRouter, HTTPException, Request
from app.services.jolpica import fetch_driver_standings
from app.models.standings import DriverStanding
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/standings/drivers/{year}", response_model=list[DriverStanding])
async def driver_standings(year: str, request: Request):
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Fetching driver standings for year {year}",
            extra={"request_id": request_id, "year": year}
        )
        
        data = await fetch_driver_standings(year)
        
        logger.info(
            f"Successfully fetched {len(data)} driver standings",
            extra={"request_id": request_id, "count": len(data)}
        )
        
        return data
        
    except httpx.HTTPError as e:
        logger.error(
            f"Upstream API error: {e}",
            extra={"request_id": request_id, "error": str(e)}
        )
        raise HTTPException(status_code=502, detail=f"Upstream API error: {e}")
        
    except Exception as e:
        logger.error(
            f"Internal error: {e}",
            extra={"request_id": request_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))
```

## Service Layer Pattern with httpx

```python
# backend/app/services/jolpica.py
import httpx
from app.cache.redis import redis_cache
from app.config import settings
import logging

logger = logging.getLogger(__name__)

_client = httpx.AsyncClient(
    base_url=settings.JOLPICA_BASE_URL,
    timeout=10.0,
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
)

@redis_cache(ttl=3600)
async def fetch_driver_standings(year: str) -> list[dict]:
    """
    Fetch driver standings for a given year from Jolpica API.
    Results are cached for 1 hour.
    """
    try:
        response = await _client.get(f"/{year}/driverStandings.json")
        response.raise_for_status()
        
        data = response.json()
        standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
        
        logger.info(f"Fetched {len(standings)} driver standings for {year}")
        return standings
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching standings: {e.response.status_code}")
        raise
    except httpx.RequestError as e:
        logger.error(f"Request error fetching standings: {e}")
        raise
    except (KeyError, IndexError) as e:
        logger.error(f"Invalid response structure: {e}")
        raise ValueError(f"Invalid API response structure: {e}")
```

## Redis Cache Decorator

```python
# backend/app/cache/redis.py
import json
import hashlib
from functools import wraps
from redis.asyncio import Redis
from typing import Any, Callable
import logging

logger = logging.getLogger(__name__)

redis_client: Redis | None = None

def redis_cache(ttl: int = 3600):
    """
    Decorator to cache function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function name and arguments
            raw = f"{func.__module__}.{func.__name__}:{args}:{sorted(kwargs.items())}"
            key = f"cache:{hashlib.md5(raw.encode()).hexdigest()}"
            
            # Try to get from cache
            if redis_client:
                try:
                    cached = await redis_client.get(key)
                    if cached:
                        logger.debug(f"Cache HIT for {func.__name__}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Cache read error: {e}")
            
            # Cache miss - execute function
            logger.debug(f"Cache MISS for {func.__name__}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            if redis_client:
                try:
                    await redis_client.setex(
                        key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                    logger.debug(f"Cached result for {func.__name__} (TTL: {ttl}s)")
                except Exception as e:
                    logger.warning(f"Cache write error: {e}")
            
            return result
        
        return wrapper
    return decorator
```

## Pydantic Models with Validation

```python
# backend/app/models/standings.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class DriverInfo(BaseModel):
    driverId: str = Field(..., description="Unique driver identifier")
    givenName: str = Field(..., description="Driver's first name")
    familyName: str = Field(..., description="Driver's last name")
    nationality: Optional[str] = Field(None, description="Driver's nationality")
    
    @field_validator('driverId')
    @classmethod
    def validate_driver_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("driverId cannot be empty")
        return v.lower()

class ConstructorInfo(BaseModel):
    constructorId: str = Field(..., description="Unique constructor identifier")
    name: str = Field(..., description="Constructor name")

class DriverStanding(BaseModel):
    position: str = Field(..., description="Championship position")
    points: str = Field(..., description="Total points")
    wins: str = Field(..., description="Number of wins")
    Driver: DriverInfo
    Constructors: list[ConstructorInfo]
    
    @field_validator('position', 'points', 'wins')
    @classmethod
    def validate_numeric_string(cls, v: str) -> str:
        try:
            int(v)
            return v
        except ValueError:
            raise ValueError(f"Must be a numeric string, got: {v}")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "position": "1",
                "points": "575",
                "wins": "19",
                "Driver": {
                    "driverId": "verstappen",
                    "givenName": "Max",
                    "familyName": "Verstappen",
                    "nationality": "Dutch"
                },
                "Constructors": [
                    {"constructorId": "red_bull", "name": "Red Bull"}
                ]
            }
        }
    }
```

## WebSocket Connection Manager

```python
# backend/app/ws/manager.py
import asyncio
import json
from fastapi import WebSocket
from app.services.openf1 import (
    fetch_live_positions,
    fetch_live_intervals,
    fetch_live_racecontrol
)
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}
        self.tasks: dict[str, asyncio.Task] = {}
    
    async def connect(self, ws: WebSocket, session_key: str):
        await ws.accept()
        self.connections.setdefault(session_key, []).append(ws)
        logger.info(f"Client connected to session {session_key}")
        
        if session_key not in self.tasks:
            self.tasks[session_key] = asyncio.create_task(
                self._poll(session_key)
            )
    
    async def disconnect(self, ws: WebSocket, session_key: str):
        if session_key in self.connections:
            self.connections[session_key].remove(ws)
            logger.info(f"Client disconnected from session {session_key}")
            
            if not self.connections[session_key]:
                # No more clients, stop polling
                if session_key in self.tasks:
                    self.tasks[session_key].cancel()
                    del self.tasks[session_key]
                del self.connections[session_key]
                logger.info(f"Stopped polling for session {session_key}")
    
    async def broadcast(self, session_key: str, data: dict):
        dead = []
        for ws in self.connections.get(session_key, []):
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                dead.append(ws)
        
        for ws in dead:
            await self.disconnect(ws, session_key)
    
    async def _poll(self, session_key: str):
        """Poll OpenF1 API and broadcast updates every 4 seconds"""
        while True:
            try:
                positions = await fetch_live_positions(session_key)
                intervals = await fetch_live_intervals(session_key)
                race_control = await fetch_live_racecontrol(session_key)
                
                await self.broadcast(session_key, {
                    "positions": positions,
                    "intervals": intervals,
                    "race_control": race_control,
                })
                
            except asyncio.CancelledError:
                logger.info(f"Polling cancelled for session {session_key}")
                break
            except Exception as e:
                logger.error(f"Poll error for {session_key}: {e}")
            
            await asyncio.sleep(4)

manager = ConnectionManager()
```
