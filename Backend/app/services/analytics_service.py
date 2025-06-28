"""
Analytics service for comprehensive business intelligence.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.clickhouse import get_clickhouse
from app.core.mongodb import get_mongodb
from app.models.property import Property, PropertyStatus, PropertyType, DealType
from app.models.user import User, UserRole
from app.models.developer import Developer
from app.models.search_history import SearchHistory
from app.models.view_history import ViewHistory
from app.models.favorite import Favorite

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Advanced analytics service for business intelligence."""
    
    def __init__(self):
        self.clickhouse = None
        self.mongodb = None
    
    async def _get_clickhouse(self):
        """Get ClickHouse manager with error handling."""
        try:
            if not self.clickhouse:
                self.clickhouse = await get_clickhouse()
            return self.clickhouse
        except Exception as e:
            logger.warning(f"ClickHouse not available: {e}")
            return None
    
    async def _get_mongodb(self):
        """Get MongoDB manager."""
        if not self.mongodb:
            self.mongodb = await get_mongodb()
        return self.mongodb
    
    # Property Analytics
    
    async def get_property_statistics(self) -> List[Dict[str, Any]]:
        """Get property statistics by status and type."""
        async for db in get_async_session():
            query = (
                select(
                    Property.status,
                    Property.property_type,
                    func.count(Property.id).label('count'),
                    func.avg(Property.price).label('avg_price'),
                    func.min(Property.price).label('min_price'),
                    func.max(Property.price).label('max_price')
                )
                .group_by(Property.status, Property.property_type)
            )
            
            result = await db.execute(query)
            return [
                {
                    'status': row.status.value if hasattr(row.status, 'value') else str(row.status),
                    'property_type': row.property_type.value if hasattr(row.property_type, 'value') else str(row.property_type),
                    'count': row.count,
                    'avg_price': float(row.avg_price) if row.avg_price else 0,
                    'min_price': float(row.min_price) if row.min_price else 0,
                    'max_price': float(row.max_price) if row.max_price else 0
                }
                for row in result
            ]
    
    async def get_property_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get property listing trends."""
        view_trends = []
        try:
            clickhouse = await self._get_clickhouse()
            if clickhouse:
                # Get view trends from ClickHouse
                view_trends = await clickhouse.get_popular_properties(days=days, limit=50)
        except Exception as e:
            logger.warning(f"Failed to get view trends from ClickHouse: {e}")
            view_trends = []
        
        # Get listing trends from PostgreSQL
        async for db in get_async_session():
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = (
                select(
                    func.date(Property.created_at).label('date'),
                    Property.property_type,
                    func.count(Property.id).label('count')
                )
                .where(Property.created_at >= start_date)
                .group_by(func.date(Property.created_at), Property.property_type)
                .order_by(func.date(Property.created_at))
            )
            
            result = await db.execute(query)
            listing_trends = [
                {
                    'date': row.date.isoformat(),
                    'property_type': row.property_type.value if hasattr(row.property_type, 'value') else str(row.property_type),
                    'count': row.count
                }
                for row in result
            ]
        
        return {
            'view_trends': view_trends,
            'listing_trends': listing_trends
        }
    
    async def get_price_analytics(self, city: Optional[str] = None, 
                                 property_type: Optional[str] = None) -> Dict[str, Any]:
        """Get price analytics and trends."""
        async for db in get_async_session():
            query = select(Property).where(Property.status == PropertyStatus.ACTIVE)
            
            if city:
                query = query.where(Property.city == city)
            if property_type:
                query = query.where(Property.property_type == property_type)
            
            result = await db.execute(query)
            properties = result.scalars().all()
            
            if not properties:
                return {'error': 'No properties found'}
            
            prices = [float(p.price) for p in properties if p.price]
            price_per_sqm = [float(p.price_per_sqm) for p in properties if p.price_per_sqm]
            
            return {
                'total_properties': len(properties),
                'price_stats': {
                    'avg': sum(prices) / len(prices) if prices else 0,
                    'min': min(prices) if prices else 0,
                    'max': max(prices) if prices else 0,
                    'median': sorted(prices)[len(prices)//2] if prices else 0
                },
                'price_per_sqm_stats': {
                    'avg': sum(price_per_sqm) / len(price_per_sqm) if price_per_sqm else 0,
                    'min': min(price_per_sqm) if price_per_sqm else 0,
                    'max': max(price_per_sqm) if price_per_sqm else 0,
                    'median': sorted(price_per_sqm)[len(price_per_sqm)//2] if price_per_sqm else 0
                }
            }
    
    # User Analytics
    
    async def get_user_statistics(self) -> List[Dict[str, Any]]:
        """Get user statistics by role and status."""
        async for db in get_async_session():
            query = (
                select(
                    User.role,
                    User.is_active.label('status'),
                    func.count(User.id).label('count')
                )
                .group_by(User.role, User.is_active)
            )
            
            result = await db.execute(query)
            return [
                {
                    'role': row.role.value if hasattr(row.role, 'value') else str(row.role),
                    'status': 'active' if row.status else 'inactive',
                    'count': row.count
                }
                for row in result
            ]
    
    async def get_user_behavior_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get user behavior analytics."""
        try:
            mongodb = await self._get_mongodb()
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get analytics from MongoDB
            from app.models.mongodb import UserAnalytics
            
            analytics = await UserAnalytics.find(
                UserAnalytics.session_start >= start_date
            ).to_list()
            
            if not analytics:
                return {'error': 'No analytics data found'}
            
            total_sessions = len(analytics)
            total_users = len(set(a.user_id for a in analytics if a.user_id))
            total_page_views = sum(a.total_page_views for a in analytics)
            total_property_views = sum(a.total_property_views for a in analytics)
            
            sessions_with_duration = [a for a in analytics if a.session_duration]
            avg_session_duration = (
                sum(a.session_duration for a in sessions_with_duration) / len(sessions_with_duration)
                if sessions_with_duration else 0
            )
            
            sessions_with_bounce = [a for a in analytics if a.bounce_rate is not None]
            avg_bounce_rate = (
                sum(a.bounce_rate for a in sessions_with_bounce) / len(sessions_with_bounce)
                if sessions_with_bounce else 0
            )
            
            return {
                'total_sessions': total_sessions,
                'unique_users': total_users,
                'total_page_views': total_page_views,
                'total_property_views': total_property_views,
                'avg_session_duration': avg_session_duration,
                'bounce_rate': avg_bounce_rate
            }
        except Exception as e:
            logger.error(f"Failed to get user behavior analytics: {e}")
            return {'error': 'Failed to retrieve user behavior data'}
    
    # Search Analytics
    
    async def get_search_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get search analytics and trends."""
        try:
            clickhouse = await self._get_clickhouse()
            # Get search trends from ClickHouse
            search_trends = await clickhouse.get_search_trends(days=days)
        except Exception:
            search_trends = []
        
        # Get search statistics from PostgreSQL
        async for db in get_async_session():
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = (
                select(
                    func.count(SearchHistory.id).label('total_searches'),
                    func.count(func.distinct(SearchHistory.user_id)).label('unique_searchers'),
                    func.avg(SearchHistory.results_count).label('avg_results')
                )
                .where(SearchHistory.created_at >= start_date)
            )
            
            result = await db.execute(query)
            stats = result.first()
            
            return {
                'total_searches': stats.total_searches if stats else 0,
                'unique_searchers': stats.unique_searchers if stats else 0,
                'avg_results_per_search': float(stats.avg_results) if stats and stats.avg_results else 0,
                'popular_queries': search_trends
            }
    
    # Developer Analytics
    
    async def get_developer_analytics(self) -> Dict[str, Any]:
        """Get developer performance analytics."""
        async for db in get_async_session():
            # Developer statistics
            dev_query = (
                select(
                    Developer.verification_status,
                    func.count(Developer.id).label('count')
                )
                .group_by(Developer.verification_status)
            )
            
            dev_result = await db.execute(dev_query)
            developer_stats = [
                {
                    'status': row.verification_status.value if hasattr(row.verification_status, 'value') else str(row.verification_status),
                    'count': row.count
                }
                for row in dev_result
            ]
            
            # Top developers by property count
            top_devs_query = (
                select(
                    Developer.company_name,
                    func.count(Property.id).label('property_count'),
                    func.avg(Property.price).label('avg_price')
                )
                .join(Property)
                .group_by(Developer.id, Developer.company_name)
                .order_by(func.count(Property.id).desc())
                .limit(10)
            )
            
            top_devs_result = await db.execute(top_devs_query)
            top_developers = [
                {
                    'company_name': row.company_name,
                    'property_count': row.property_count,
                    'avg_price': float(row.avg_price) if row.avg_price else 0
                }
                for row in top_devs_result
            ]
            
            return {
                'developer_statistics': developer_stats,
                'top_developers': top_developers
            }
    
    # Geographic Analytics
    
    async def get_geographic_analytics(self) -> Dict[str, Any]:
        """Get geographic distribution analytics."""
        async for db in get_async_session():
            # Properties by city
            city_query = (
                select(
                    Property.city,
                    func.count(Property.id).label('property_count'),
                    func.avg(Property.price).label('avg_price')
                )
                .where(Property.status == PropertyStatus.ACTIVE)
                .group_by(Property.city)
                .order_by(func.count(Property.id).desc())
            )
            
            city_result = await db.execute(city_query)
            city_stats = [
                {
                    'city': row.city,
                    'property_count': row.property_count,
                    'avg_price': float(row.avg_price) if row.avg_price else 0
                }
                for row in city_result
            ]
            
            return {
                'cities': city_stats
            }
    
    # Engagement Analytics
    
    async def get_engagement_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get user engagement analytics."""
        async for db in get_async_session():
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Favorites analytics
            favorites_query = (
                select(
                    func.count(Favorite.id).label('total_favorites'),
                    func.count(func.distinct(Favorite.user_id)).label('users_with_favorites')
                )
                .where(Favorite.created_at >= start_date)
            )
            
            favorites_result = await db.execute(favorites_query)
            favorites_stats = favorites_result.first()
            
            # View analytics
            views_query = (
                select(
                    func.count(ViewHistory.id).label('total_views'),
                    func.count(func.distinct(ViewHistory.user_id)).label('unique_viewers')
                )
                .where(ViewHistory.created_at >= start_date)
            )
            
            views_result = await db.execute(views_query)
            views_stats = views_result.first()
            
            return {
                'favorites': {
                    'total': favorites_stats.total_favorites if favorites_stats else 0,
                    'unique_users': favorites_stats.users_with_favorites if favorites_stats else 0
                },
                'views': {
                    'total': views_stats.total_views if views_stats else 0,
                    'unique_viewers': views_stats.unique_viewers if views_stats else 0
                }
            }
    
    # Performance Analytics
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get application performance analytics."""
        try:
            mongodb = await self._get_mongodb()
            
            from app.models.mongodb import PerformanceMetric
            
            # Get recent performance metrics
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(hours=24)
            
            metrics = await PerformanceMetric.find(
                PerformanceMetric.timestamp >= start_date
            ).to_list()
            
            if not metrics:
                return {'error': 'No performance data found'}
            
            # Group by endpoint
            endpoint_metrics = {}
            for metric in metrics:
                endpoint = metric.endpoint or 'unknown'
                if endpoint not in endpoint_metrics:
                    endpoint_metrics[endpoint] = []
                endpoint_metrics[endpoint].append(metric.value)
            
            # Calculate averages
            performance_data = []
            for endpoint, values in endpoint_metrics.items():
                performance_data.append({
                    'endpoint': endpoint,
                    'avg_response_time': sum(values) / len(values),
                    'min_response_time': min(values),
                    'max_response_time': max(values),
                    'total_requests': len(values)
                })
            
            return {
                'endpoint_performance': sorted(
                    performance_data, 
                    key=lambda x: x['avg_response_time'], 
                    reverse=True
                )
            }
        except Exception as e:
            logger.error(f"Failed to get performance analytics: {e}")
            return {'error': 'Failed to retrieve performance data'}
    
    async def get_comprehensive_dashboard(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard data."""
        try:
            # Get all analytics
            property_stats = await self.get_property_statistics()
            user_stats = await self.get_user_statistics()
            search_analytics = await self.get_search_analytics(days)
            engagement_analytics = await self.get_engagement_analytics(days)
            geographic_analytics = await self.get_geographic_analytics()
            
            return {
                'summary': {
                    'total_properties': sum(stat['count'] for stat in property_stats),
                    'total_users': sum(stat['count'] for stat in user_stats),
                    'total_searches': search_analytics.get('total_searches', 0),
                    'total_views': engagement_analytics.get('views', {}).get('total', 0)
                },
                'property_statistics': property_stats,
                'user_statistics': user_stats,
                'search_analytics': search_analytics,
                'engagement_analytics': engagement_analytics,
                'geographic_analytics': geographic_analytics,
                'generated_at': datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating dashboard: {e}")
            return {'error': str(e)}
