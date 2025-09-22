"""
FastAPI WSAP Dependencies

Reusable dependencies for WSAP integration.
"""

import logging
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security scheme for API documentation
security = HTTPBearer()


async def get_wsap_client(request: Request):
    """
    Dependency to get the WSAP client from app state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        WSAP client instance
        
    Raises:
        HTTPException: If client is not configured
    """
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(
            status_code=503,
            detail="WSAP client not configured"
        )
    
    return client


async def get_wsap_config(request: Request):
    """
    Dependency to get the WSAP configuration.
    
    Args:
        request: FastAPI request object
        
    Returns:
        WSAP configuration instance
    """
    return request.app.state.wsap_config


async def require_wsap_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    client = Depends(get_wsap_client)
) -> Dict[str, Any]:
    """
    Dependency to require WSAP authentication.
    
    Args:
        credentials: Bearer token credentials
        client: WSAP client instance
        
    Returns:
        Authenticated user/entity information
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    try:
        # Validate token with WSAP API
        auth_info = client.validate_token(token)
        
        if not auth_info:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        
        return auth_info
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


async def optional_wsap_auth(
    authorization: Optional[str] = Header(None),
    client = Depends(get_wsap_client)
) -> Optional[Dict[str, Any]]:
    """
    Optional WSAP authentication dependency.
    
    Args:
        authorization: Optional Authorization header
        client: WSAP client instance
        
    Returns:
        Authenticated user/entity information or None
    """
    if not authorization:
        return None
    
    # Parse Bearer token
    if not authorization.startswith("Bearer "):
        return None
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    try:
        auth_info = client.validate_token(token)
        return auth_info
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None


async def get_entity_id(
    entity_id: Optional[str] = None,
    config = Depends(get_wsap_config)
) -> str:
    """
    Get entity ID from parameter or configuration.
    
    Args:
        entity_id: Optional entity ID parameter
        config: WSAP configuration
        
    Returns:
        Entity ID
        
    Raises:
        HTTPException: If no entity ID is available
    """
    entity_id = entity_id or config.entity_id
    
    if not entity_id:
        raise HTTPException(
            status_code=400,
            detail="Entity ID is required"
        )
    
    return entity_id


async def get_disclosure_level(
    x_wsap_disclosure_level: Optional[str] = Header(None, alias="X-WSAP-Disclosure-Level")
) -> str:
    """
    Get disclosure level from request header.
    
    Args:
        x_wsap_disclosure_level: Disclosure level header
        
    Returns:
        Disclosure level (defaults to 'standard')
    """
    valid_levels = ["basic", "standard", "detailed", "complete"]
    
    if x_wsap_disclosure_level and x_wsap_disclosure_level.lower() in valid_levels:
        return x_wsap_disclosure_level.lower()
    
    return "standard"


async def verify_domain_ownership(
    domain: str,
    client = Depends(get_wsap_client)
) -> bool:
    """
    Verify domain ownership via DNS TXT record.
    
    Args:
        domain: Domain to verify
        client: WSAP client instance
        
    Returns:
        True if verified, False otherwise
    """
    try:
        return client.verify_domain(domain)
    except Exception as e:
        logger.error(f"Domain verification failed for {domain}: {e}")
        return False


class WSAPRateLimiter:
    """
    Rate limiting dependency for WSAP endpoints.
    """
    
    def __init__(self, max_requests: int = 60, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_counts: Dict[str, list] = {}
    
    async def __call__(self, request: Request):
        """
        Check rate limit for request.
        
        Args:
            request: FastAPI request
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        from datetime import datetime, timedelta
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for proxy headers
        if "X-Forwarded-For" in request.headers:
            client_ip = request.headers["X-Forwarded-For"].split(",")[0].strip()
        elif "X-Real-IP" in request.headers:
            client_ip = request.headers["X-Real-IP"]
        
        now = datetime.utcnow()
        
        # Clean old entries
        if client_ip in self.request_counts:
            cutoff = now - timedelta(seconds=self.time_window)
            self.request_counts[client_ip] = [
                t for t in self.request_counts[client_ip] if t > cutoff
            ]
        
        # Check rate limit
        if client_ip in self.request_counts:
            if len(self.request_counts[client_ip]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": self.time_window
                    }
                )
        
        # Record request
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        self.request_counts[client_ip].append(now)


# Create default rate limiter instance
wsap_rate_limiter = WSAPRateLimiter()