"""
Main API router for version 1.
"""

from fastapi import APIRouter

# Import endpoint routers
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.developers import router as developers_router
from app.api.v1.endpoints.properties import router as properties_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.favorites import router as favorites_router
from app.api.v1.endpoints.reviews import router as reviews_router
from app.api.v1.endpoints.leads import router as leads_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(developers_router, prefix="/developers", tags=["Developers"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(properties_router, prefix="/properties", tags=["Properties"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(favorites_router, prefix="/favorites", tags=["Favorites"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(leads_router, prefix="/leads", tags=["Leads"])


# Basic health check endpoint
@api_router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


@api_router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Real Estate Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
    }
