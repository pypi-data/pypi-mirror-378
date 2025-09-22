"""
FastAPI WSAP Application

Main FastAPI application class for WSAP integration.
"""

import logging
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .routers import wsap_router
from .middleware import WSAPMiddleware
from .config import WSAPConfig

try:
    from ltfi_wsap import WSAPClient
except ImportError:
    WSAPClient = None

logger = logging.getLogger(__name__)


class WSAPApp:
    """
    FastAPI application with WSAP integration.
    
    Usage:
        app = WSAPApp(
            api_key="your-api-key",
            entity_id="your-entity-id"
        )
        
        # Access the FastAPI instance
        fastapi_app = app.app
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.ltfi.ai",
        entity_id: Optional[str] = None,
        title: str = "WSAP-Enabled API",
        description: str = "FastAPI application with WSAP integration",
        version: str = "1.0.0",
        **kwargs
    ):
        """Initialize the WSAP FastAPI application."""
        self.config = WSAPConfig(
            api_key=api_key,
            base_url=base_url,
            entity_id=entity_id
        )
        
        self.client: Optional['WSAPClient'] = None
        
        # Initialize WSAP client if SDK is available
        if WSAPClient and api_key:
            self.client = WSAPClient(
                api_key=api_key,
                base_url=base_url,
                entity_id=entity_id
            )
        
        # Create FastAPI app with lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info("Starting WSAP-enabled FastAPI application")
            app.state.wsap_client = self.client
            app.state.wsap_config = self.config
            yield
            # Shutdown
            logger.info("Shutting down WSAP-enabled FastAPI application")
        
        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
            lifespan=lifespan,
            **kwargs
        )
        
        # Add middleware
        self._setup_middleware()
        
        # Include routers
        self._setup_routers()
        
        # Add WSAP endpoint
        self._setup_wsap_endpoint()
    
    def _setup_middleware(self):
        """Configure application middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # WSAP middleware
        self.app.add_middleware(WSAPMiddleware, config=self.config)
    
    def _setup_routers(self):
        """Include application routers."""
        self.app.include_router(
            wsap_router,
            prefix="/wsap",
            tags=["wsap"]
        )
    
    def _setup_wsap_endpoint(self):
        """Setup the /.well-known/wsap.json endpoint."""
        
        @self.app.get("/.well-known/wsap.json", tags=["wsap"])
        async def serve_wsap_json(request: Request):
            """Serve the WSAP JSON file."""
            if not self.client:
                raise HTTPException(
                    status_code=503,
                    detail="WSAP client not configured"
                )
            
            try:
                # Get entity data
                entity_id = self.config.entity_id
                if not entity_id:
                    raise HTTPException(
                        status_code=500,
                        detail="No entity ID configured"
                    )
                
                wsap_data = await self.get_wsap_data(entity_id)
                
                # Add cache headers
                response = JSONResponse(content=wsap_data)
                response.headers["Cache-Control"] = f"public, max-age={self.config.cache_timeout}"
                
                return response
                
            except Exception as e:
                logger.error(f"Error serving WSAP data: {e}")
                raise HTTPException(
                    status_code=500,
                    detail="Error generating WSAP data"
                )
    
    async def get_wsap_data(self, entity_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get WSAP data for an entity.
        
        Args:
            entity_id: Optional entity ID
            
        Returns:
            WSAP data dictionary
        """
        if not self.client:
            raise ValueError("WSAP client not initialized")
        
        entity_id = entity_id or self.config.entity_id
        if not entity_id:
            raise ValueError("No entity ID provided")
        
        try:
            # In a real implementation, this would be async
            wsap_data = self.client.get_entity(entity_id)
            
            # Add metadata
            wsap_data['_metadata'] = {
                'generated_at': datetime.utcnow().isoformat(),
                'source': 'fastapi-ltfi-wsap',
                'version': '2.0.0'
            }
            
            return wsap_data
            
        except Exception as e:
            logger.error(f"Error fetching WSAP data: {e}")
            raise
    
    def mount_app(self, path: str, app: FastAPI, name: str = None):
        """
        Mount a sub-application.
        
        Args:
            path: Path to mount the app at
            app: FastAPI app to mount
            name: Optional name for the mount
        """
        self.app.mount(path, app, name=name)
    
    def add_api_route(self, *args, **kwargs):
        """Add an API route to the application."""
        return self.app.add_api_route(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        """Add a GET route."""
        return self.app.get(*args, **kwargs)
    
    def post(self, *args, **kwargs):
        """Add a POST route."""
        return self.app.post(*args, **kwargs)
    
    def put(self, *args, **kwargs):
        """Add a PUT route."""
        return self.app.put(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Add a DELETE route."""
        return self.app.delete(*args, **kwargs)
    
    def patch(self, *args, **kwargs):
        """Add a PATCH route."""
        return self.app.patch(*args, **kwargs)


# Convenience function to create a WSAP-enabled FastAPI app
def create_wsap_app(
    api_key: Optional[str] = None,
    entity_id: Optional[str] = None,
    **kwargs
) -> FastAPI:
    """
    Create a WSAP-enabled FastAPI application.
    
    Args:
        api_key: WSAP API key
        entity_id: Default entity ID
        **kwargs: Additional FastAPI arguments
        
    Returns:
        FastAPI application instance
    """
    wsap_app = WSAPApp(
        api_key=api_key,
        entity_id=entity_id,
        **kwargs
    )
    return wsap_app.app


from datetime import datetime