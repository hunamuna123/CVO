"""
Main API router for version 1.
"""

from fastapi import APIRouter

# Import endpoint routers
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.bookings import router as bookings_router
from app.api.v1.endpoints.complexes import router as complexes_router
from app.api.v1.endpoints.developers import router as developers_router
from app.api.v1.endpoints.favorites import router as favorites_router
from app.api.v1.endpoints.leads import router as leads_router
from app.api.v1.endpoints.properties import router as properties_router
from app.api.v1.endpoints.promo_codes import router as promo_codes_router
from app.api.v1.endpoints.reviews import router as reviews_router
from app.api.v1.endpoints.users import router as users_router

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth_router, tags=["Authentication"])
api_router.include_router(developers_router, tags=["Developers"])
api_router.include_router(users_router, tags=["Users"])
api_router.include_router(properties_router, tags=["Properties"])
api_router.include_router(complexes_router, tags=["Complexes"])
api_router.include_router(bookings_router, tags=["Bookings"])
api_router.include_router(promo_codes_router, tags=["Promo Codes"])
api_router.include_router(analytics_router, tags=["Analytics"])
api_router.include_router(ai_router, tags=["AI Services"])
api_router.include_router(favorites_router, tags=["Favorites"])
api_router.include_router(reviews_router, tags=["Reviews"])
api_router.include_router(leads_router, tags=["Leads"])


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
