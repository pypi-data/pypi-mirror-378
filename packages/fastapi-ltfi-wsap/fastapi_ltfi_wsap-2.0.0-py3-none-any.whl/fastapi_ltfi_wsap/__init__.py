"""
FastAPI LTFI-WSAP Integration

FastAPI application for integrating LTFI-WSAP (Layered Transformer Framework Intelligence - 
Web System Alignment Protocol).
"""

__version__ = "2.0.0"

from .app import WSAPApp
from .routers import wsap_router
from .middleware import WSAPMiddleware
from .dependencies import get_wsap_client, require_wsap_auth

__all__ = [
    'WSAPApp',
    'wsap_router',
    'WSAPMiddleware',
    'get_wsap_client',
    'require_wsap_auth'
]