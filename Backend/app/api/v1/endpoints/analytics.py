"""
Analytics API endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.utils.security import get_current_user, get_current_admin_user
from app.models.user import User

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_analytics_dashboard(
    days: int = Query(7, ge=1, le=90, description="Number of days for analytics"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get comprehensive analytics dashboard.
    Requires admin privileges.
    """
    analytics_service = AnalyticsService()
    return await analytics_service.get_comprehensive_dashboard(days=days)


@router.get("/properties", response_model=Dict[str, Any])
async def get_property_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days for trends"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get property analytics including statistics and trends.
    """
    analytics_service = AnalyticsService()
    
    # Get property statistics and trends
    statistics = await analytics_service.get_property_statistics()
    trends = await analytics_service.get_property_trends(days=days)
    
    return {
        "statistics": statistics,
        "trends": trends
    }


@router.get("/users", response_model=Dict[str, Any])
async def get_user_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days for behavior analytics"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get user analytics including statistics and behavior.
    """
    analytics_service = AnalyticsService()
    
    # Get user statistics and behavior
    statistics = await analytics_service.get_user_statistics()
    behavior = await analytics_service.get_user_behavior_analytics(days=days)
    
    return {
        "statistics": statistics,
        "behavior": behavior
    }


@router.get("/search", response_model=Dict[str, Any])
async def get_search_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days for search analytics"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get search analytics and trends.
    """
    analytics_service = AnalyticsService()
    return await analytics_service.get_search_analytics(days=days)


@router.get("/developers", response_model=Dict[str, Any])
async def get_developer_analytics(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get developer performance analytics.
    """
    analytics_service = AnalyticsService()
    return await analytics_service.get_developer_analytics()


@router.get("/geographic", response_model=Dict[str, Any])
async def get_geographic_analytics(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get geographic distribution analytics.
    """
    analytics_service = AnalyticsService()
    return await analytics_service.get_geographic_analytics()


@router.get("/engagement", response_model=Dict[str, Any])
async def get_engagement_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days for engagement analytics"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get user engagement analytics.
    """
    analytics_service = AnalyticsService()
    return await analytics_service.get_engagement_analytics(days=days)


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_analytics(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get application performance analytics.
    """
    analytics_service = AnalyticsService()
    return await analytics_service.get_performance_analytics()


@router.get("/prices", response_model=Dict[str, Any])
async def get_price_analytics(
    city: Optional[str] = Query(None, description="Filter by city"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    current_user: User = Depends(get_current_user)
):
    """
    Get price analytics and trends.
    Public endpoint with optional filters.
    """
    analytics_service = AnalyticsService()
    return await analytics_service.get_price_analytics(
        city=city,
        property_type=property_type
    )


@router.get("/popular-searches", response_model=Dict[str, Any])
async def get_popular_searches(
    days: int = Query(7, ge=1, le=30, description="Number of days for popular searches"),
):
    """
    Get popular search queries.
    Public endpoint for showing trending searches.
    """
    try:
        from app.core.clickhouse import get_clickhouse
        
        clickhouse = await get_clickhouse()
        search_trends = await clickhouse.get_search_trends(days=days)
        
        return {
            "popular_searches": search_trends,
            "period_days": days
        }
    except Exception as e:
        logger.warning(f"Failed to get popular searches: {e}")
        return {
            "popular_searches": [],
            "period_days": days,
            "note": "Analytics data temporarily unavailable"
        }


@router.get("/popular-properties", response_model=Dict[str, Any])
async def get_popular_properties(
    days: int = Query(7, ge=1, le=30, description="Number of days for popular properties"),
    limit: int = Query(10, ge=1, le=50, description="Number of properties to return")
):
    """
    Get most viewed properties.
    Public endpoint for showing trending properties.
    """
    try:
        from app.core.clickhouse import get_clickhouse
        
        clickhouse = await get_clickhouse()
        popular_properties = await clickhouse.get_popular_properties(days=days, limit=limit)
        
        return {
            "popular_properties": popular_properties,
            "period_days": days
        }
    except Exception as e:
        logger.warning(f"Failed to get popular properties: {e}")
        return {
            "popular_properties": [],
            "period_days": days,
            "note": "Analytics data temporarily unavailable"
        }
