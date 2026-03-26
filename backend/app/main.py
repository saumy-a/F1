"""
FastAPI application entry point with lifespan management.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings, configure_logging
from app.cache.redis import init_redis, close_redis
from app.middleware.request_id import RequestIDMiddleware

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles Redis connection initialization and cleanup.
    """
    # Startup
    logger.info("Starting F1 Dashboard API...")
    try:
        await init_redis()
        logger.info("Redis connection initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        # Continue without Redis - caching will be disabled
    
    yield
    
    # Shutdown
    logger.info("Shutting down F1 Dashboard API...")
    try:
        await close_redis()
        logger.info("Redis connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI backend for F1 Dashboard with real-time race tracking",
    lifespan=lifespan
)

# Add middleware (order matters!)
# Request ID middleware should be first for tracing
app.add_middleware(RequestIDMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns application status and version.
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "F1 Dashboard API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
from app.routers import standings, races, analytics, live, ws

app.include_router(standings.router, prefix="/api", tags=["standings"])
app.include_router(races.router, prefix="/api", tags=["races"])
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(live.router, prefix="/api", tags=["live"])
app.include_router(ws.router, prefix="/ws", tags=["websocket"])
