"""
Main API v1 router.
"""
from fastapi import APIRouter

from turtle_db.api.v1.endpoints import items

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(items.router, prefix="/v1/items", tags=["items"])

# Health check for API
@api_router.get("/v1/health", tags=["health"])
async def api_health():
    """API health check."""
    return {"status": "healthy", "version": "v1"}