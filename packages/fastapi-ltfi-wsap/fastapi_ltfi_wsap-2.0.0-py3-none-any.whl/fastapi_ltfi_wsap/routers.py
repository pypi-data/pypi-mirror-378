"""
FastAPI WSAP Routers

API routes for WSAP functionality.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Query, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .dependencies import get_wsap_client, require_wsap_auth
from .models import (
    WSAPEntity,
    CreateEntityRequest,
    UpdateEntityRequest,
    VerifyDomainRequest,
    GenerateWSAPRequest,
    EntityResponse,
    VerificationResponse,
    WSAPResponse
)

logger = logging.getLogger(__name__)

# Create router
wsap_router = APIRouter()


# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>WSAP Dashboard</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #333; }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .entity {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #ddd;
            border-radius: 4px;
        }
        .entity.verified { border-left-color: #4CAF50; }
        .entity.unverified { border-left-color: #FFC107; }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge.verified { background: #4CAF50; color: white; }
        .badge.unverified { background: #FFC107; color: #333; }
        .status { color: #666; font-size: 14px; }
        .api-info { 
            background: #f9f9f9;
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 WSAP Dashboard</h1>
        
        <div class="card">
            <h2>Configuration Status</h2>
            <div class="api-info">
                <strong>API Status:</strong> <span id="api-status">Checking...</span><br>
                <strong>Base URL:</strong> {base_url}<br>
                <strong>Entity ID:</strong> {entity_id}<br>
                <strong>WSAP Endpoint:</strong> <a href="/.well-known/wsap.json">/.well-known/wsap.json</a>
            </div>
        </div>
        
        <div class="card">
            <h2>Entities</h2>
            <div id="entities-list">Loading...</div>
        </div>
        
        <div class="card">
            <h2>API Documentation</h2>
            <p>Explore the API documentation:</p>
            <ul>
                <li><a href="/docs">Swagger UI</a></li>
                <li><a href="/redoc">ReDoc</a></li>
            </ul>
        </div>
    </div>
    
    <script>
        // Check API status
        fetch('/wsap/health')
            .then(res => res.json())
            .then(data => {{
                document.getElementById('api-status').textContent = 
                    data.api_reachable ? '✅ Connected' : '⚠️ Not connected';
            }})
            .catch(() => {{
                document.getElementById('api-status').textContent = '❌ Error';
            }});
        
        // Load entities
        fetch('/wsap/api/entities')
            .then(res => res.json())
            .then(data => {{
                const container = document.getElementById('entities-list');
                if (data.entities && data.entities.length > 0) {{
                    container.innerHTML = data.entities.map(entity => `
                        <div class="entity ${{entity.domain_verified ? 'verified' : 'unverified'}}">
                            <h3>${{entity.name}}</h3>
                            <span class="badge ${{entity.domain_verified ? 'verified' : 'unverified'}}">
                                ${{entity.domain_verified ? 'Verified' : 'Unverified'}}
                            </span>
                            <div class="status">
                                <strong>ID:</strong> ${{entity.wsap_id}}<br>
                                <strong>Type:</strong> ${{entity.entity_type}}<br>
                                <strong>Domain:</strong> ${{entity.primary_domain}}
                            </div>
                        </div>
                    `).join('');
                }} else {{
                    container.innerHTML = '<p>No entities found.</p>';
                }}
            }})
            .catch(() => {{
                document.getElementById('entities-list').innerHTML = 
                    '<p>Error loading entities.</p>';
            }});
    </script>
</body>
</html>
"""


@wsap_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Display WSAP dashboard."""
    config = request.app.state.wsap_config
    
    html = DASHBOARD_HTML.format(
        base_url=config.base_url,
        entity_id=config.entity_id or "Not configured"
    )
    
    return HTMLResponse(content=html)


@wsap_router.get("/api/entities", response_model=List[EntityResponse])
async def list_entities(
    request: Request,
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """List all entities with optional filters."""
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(status_code=503, detail="WSAP client not configured")
    
    try:
        # Build filters
        filters = {}
        if entity_type:
            filters['entity_type'] = entity_type
        if verified is not None:
            filters['verified'] = verified
        filters['limit'] = limit
        filters['offset'] = offset
        
        # Get entities
        entities = client.list_entities(**filters)
        
        return {
            "entities": entities,
            "count": len(entities),
            "filters": filters
        }
        
    except Exception as e:
        logger.error(f"Error listing entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@wsap_router.get("/api/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str, request: Request):
    """Get a specific entity by ID."""
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(status_code=503, detail="WSAP client not configured")
    
    try:
        entity = client.get_entity(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@wsap_router.post("/api/entities", response_model=EntityResponse, status_code=201)
async def create_entity(
    entity: CreateEntityRequest,
    request: Request,
    _: None = Depends(require_wsap_auth)
):
    """Create a new entity."""
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(status_code=503, detail="WSAP client not configured")
    
    try:
        created_entity = client.create_entity(entity.dict())
        return created_entity
        
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@wsap_router.put("/api/entities/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: str,
    updates: UpdateEntityRequest,
    request: Request,
    _: None = Depends(require_wsap_auth)
):
    """Update an entity."""
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(status_code=503, detail="WSAP client not configured")
    
    try:
        updated_entity = client.update_entity(entity_id, updates.dict(exclude_unset=True))
        if not updated_entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return updated_entity
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@wsap_router.delete("/api/entities/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: str,
    request: Request,
    _: None = Depends(require_wsap_auth)
):
    """Delete an entity."""
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(status_code=503, detail="WSAP client not configured")
    
    try:
        success = client.delete_entity(entity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@wsap_router.post("/api/verify-domain", response_model=VerificationResponse)
async def verify_domain(
    verification: VerifyDomainRequest,
    request: Request,
    _: None = Depends(require_wsap_auth)
):
    """Verify domain ownership via DNS TXT record."""
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(status_code=503, detail="WSAP client not configured")
    
    try:
        verified = client.verify_domain(verification.domain)
        
        return {
            "domain": verification.domain,
            "verified": verified,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error verifying domain {verification.domain}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@wsap_router.post("/api/generate", response_model=WSAPResponse)
async def generate_wsap(
    generate: GenerateWSAPRequest,
    request: Request
):
    """Generate WSAP JSON for an entity."""
    client = request.app.state.wsap_client
    
    if not client:
        raise HTTPException(status_code=503, detail="WSAP client not configured")
    
    try:
        entity = client.get_entity(generate.entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Apply disclosure level filtering
        if generate.disclosure_level in ['basic', 'minimal']:
            # Filter to basic fields only
            wsap_data = {
                'wsap_version': '2.0',
                'entity': {
                    'name': entity.get('name'),
                    'type': entity.get('entity_type'),
                    'primary_domain': entity.get('primary_domain')
                },
                '_metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'disclosure_level': generate.disclosure_level,
                    'source': 'fastapi-ltfi-wsap'
                }
            }
        else:
            # Full entity data
            wsap_data = {
                'wsap_version': '2.0',
                'entity': entity,
                '_metadata': {
                    'generated_at': datetime.utcnow().isoformat(),
                    'disclosure_level': generate.disclosure_level,
                    'source': 'fastapi-ltfi-wsap'
                }
            }
        
        return wsap_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating WSAP for entity {generate.entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@wsap_router.get("/health")
async def health_check(request: Request):
    """Health check endpoint."""
    client = request.app.state.wsap_client
    
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "wsap_configured": bool(client),
        "api_reachable": False
    }
    
    # Check API connectivity
    if client:
        try:
            client.list_entities(limit=1)
            status["api_reachable"] = True
        except Exception:
            status["status"] = "degraded"
    
    return status