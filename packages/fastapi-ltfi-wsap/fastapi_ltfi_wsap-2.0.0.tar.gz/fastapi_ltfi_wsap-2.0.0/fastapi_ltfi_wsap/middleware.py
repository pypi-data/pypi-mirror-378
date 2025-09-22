"""
FastAPI WSAP Middleware

Middleware for WSAP integration in FastAPI applications.
"""

import logging
from typing import Optional, Dict, Any
import json

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .config import WSAPConfig

logger = logging.getLogger(__name__)


class WSAPMiddleware(BaseHTTPMiddleware):
    """
    Middleware for WSAP integration.
    
    Handles:
    - WSAP endpoint serving
    - WSAP headers injection
    - Request/response logging
    - Rate limiting
    """
    
    def __init__(self, app, config: Optional[WSAPConfig] = None, **kwargs):
        """
        Initialize WSAP middleware.
        
        Args:
            app: FastAPI application
            config: WSAP configuration
            **kwargs: Additional configuration options
        """
        super().__init__(app)
        
        self.config = config or WSAPConfig(**kwargs)
        self.wsap_endpoint = self.config.wsap_endpoint
        self.add_headers = self.config.add_headers
    
    async def dispatch(self, request: Request, call_next):
        """
        Process requests and responses.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response object
        """
        # Log request if enabled
        if self.config.log_requests:
            logger.debug(f"WSAP Request: {request.method} {request.url.path}")
        
        # Handle WSAP endpoint
        if request.url.path == self.wsap_endpoint:
            return await self.handle_wsap_endpoint(request)
        
        # Process request normally
        response = await call_next(request)
        
        # Add WSAP headers if enabled
        if self.add_headers:
            response.headers["X-WSAP-Version"] = "2.0"
            response.headers["X-WSAP-Provider"] = "fastapi-ltfi-wsap"
            
            if self.config.entity_id:
                response.headers["X-WSAP-Entity"] = self.config.entity_id
        
        return response
    
    async def handle_wsap_endpoint(self, request: Request) -> Response:
        """
        Handle requests to the WSAP endpoint.
        
        Args:
            request: Incoming request
            
        Returns:
            JSON response with WSAP data
        """
        try:
            # Get WSAP client from app state
            client = request.app.state.wsap_client
            
            if not client:
                return JSONResponse(
                    status_code=503,
                    content={"error": "WSAP client not configured"}
                )
            
            # Get entity ID from config or query parameter
            entity_id = request.query_params.get("entity_id") or self.config.entity_id
            
            if not entity_id:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Entity ID required"}
                )
            
            # Get WSAP data
            wsap_data = client.get_entity(entity_id)
            
            if not wsap_data:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Entity not found"}
                )
            
            # Add metadata
            wsap_data["_metadata"] = {
                "generated_at": datetime.utcnow().isoformat(),
                "source": "fastapi-ltfi-wsap",
                "version": "2.0.0"
            }
            
            # Create response with cache headers
            response = JSONResponse(content=wsap_data)
            response.headers["Cache-Control"] = f"public, max-age={self.config.cache_timeout}"
            response.headers["Content-Type"] = "application/json"
            
            return response
            
        except Exception as e:
            logger.error(f"Error serving WSAP data: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Error generating WSAP data"}
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for WSAP endpoints.
    """
    
    def __init__(self, app, max_requests: int = 60, time_window: int = 60):
        """
        Initialize rate limiting middleware.
        
        Args:
            app: FastAPI application
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_counts: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        """
        Check rate limits and process request.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response object
        """
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Check X-Forwarded-For header for proxy situations
        if "X-Forwarded-For" in request.headers:
            client_id = request.headers["X-Forwarded-For"].split(",")[0].strip()
        elif "X-Real-IP" in request.headers:
            client_id = request.headers["X-Real-IP"]
        
        # Current timestamp
        now = datetime.utcnow()
        
        # Clean old entries
        if client_id in self.request_counts:
            cutoff = now - timedelta(seconds=self.time_window)
            self.request_counts[client_id] = [
                t for t in self.request_counts[client_id] if t > cutoff
            ]
        
        # Check rate limit
        if client_id in self.request_counts:
            if len(self.request_counts[client_id]) >= self.max_requests:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": self.time_window
                    }
                )
        
        # Record request
        if client_id not in self.request_counts:
            self.request_counts[client_id] = []
        self.request_counts[client_id].append(now)
        
        # Process request
        return await call_next(request)


from datetime import datetime, timedelta