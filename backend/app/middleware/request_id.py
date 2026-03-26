"""
Request ID middleware for distributed tracing.
Adds unique request ID to each request for tracking across services.
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request for distributed tracing.
    
    The request ID can be:
    - Provided by the client via X-Request-ID header
    - Generated automatically if not provided
    
    The request ID is:
    - Stored in request.state.request_id for access in route handlers
    - Added to response headers as X-Request-ID
    - Included in all log messages for the request
    """
    
    async def dispatch(self, request: Request, call_next):
        # Get request ID from header or generate new one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Store in request state for access in route handlers
        request.state.request_id = request_id
        
        # Log incoming request with ID
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(
                f"Request {request_id} failed: {e}",
                extra={"request_id": request_id, "error": str(e)},
                exc_info=True
            )
            raise
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Log response with ID
        logger.info(
            f"Response {request_id}: {response.status_code}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code
            }
        )
        
        return response
