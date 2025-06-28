"""
Prometheus metrics and monitoring configuration.
"""

import logging
import time
from typing import Any, Dict, Optional

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, multiprocess, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Create a custom registry for multiprocess mode
REGISTRY = CollectorRegistry()

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=REGISTRY
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=REGISTRY
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections',
    registry=REGISTRY
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections',
    ['database_type'],
    registry=REGISTRY
)

CACHE_OPERATIONS = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result'],
    registry=REGISTRY
)

BUSINESS_METRICS = Counter(
    'business_events_total',
    'Business events counter',
    ['event_type', 'status'],
    registry=REGISTRY
)

PROPERTY_METRICS = Gauge(
    'properties_total',
    'Total number of properties',
    ['status', 'property_type'],
    registry=REGISTRY
)

USER_METRICS = Gauge(
    'users_total',
    'Total number of users',
    ['role', 'status'],
    registry=REGISTRY
)

SEARCH_METRICS = Counter(
    'searches_total',
    'Total number of searches',
    ['has_results'],
    registry=REGISTRY
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Increment active connections
        ACTIVE_CONNECTIONS.inc()
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract metrics labels
            method = request.method
            endpoint = self._get_endpoint_name(request)
            status_code = str(response.status_code)
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=self._get_endpoint_name(request),
                status_code="500"
            ).inc()
            
            raise
        finally:
            # Decrement active connections
            ACTIVE_CONNECTIONS.dec()
    
    def _get_endpoint_name(self, request: Request) -> str:
        """Extract endpoint name from request."""
        if hasattr(request, 'url') and request.url.path:
            path = request.url.path
            # Remove API version and query parameters
            if path.startswith('/api/v1/'):
                path = path[8:]  # Remove '/api/v1/'
            # Normalize path parameters
            path_parts = path.split('/')
            normalized_parts = []
            for part in path_parts:
                if part and part.replace('-', '').replace('_', '').isalnum() and len(part) > 10:
                    # Likely an ID, replace with placeholder
                    normalized_parts.append('{id}')
                else:
                    normalized_parts.append(part)
            return '/'.join(normalized_parts)
        return 'unknown'


class MetricsCollector:
    """Business metrics collector."""
    
    @staticmethod
    def record_user_action(action_type: str, success: bool = True):
        """Record user action metrics."""
        status = "success" if success else "error"
        BUSINESS_METRICS.labels(
            event_type=f"user_{action_type}",
            status=status
        ).inc()
    
    @staticmethod
    def record_property_action(action_type: str, success: bool = True):
        """Record property action metrics."""
        status = "success" if success else "error"
        BUSINESS_METRICS.labels(
            event_type=f"property_{action_type}",
            status=status
        ).inc()
    
    @staticmethod
    def record_search(has_results: bool):
        """Record search metrics."""
        SEARCH_METRICS.labels(
            has_results="yes" if has_results else "no"
        ).inc()
    
    @staticmethod
    def record_cache_operation(operation: str, hit: bool):
        """Record cache operation metrics."""
        result = "hit" if hit else "miss"
        CACHE_OPERATIONS.labels(
            operation=operation,
            result=result
        ).inc()
    
    @staticmethod
    def update_database_connections(db_type: str, count: int):
        """Update database connection metrics."""
        DATABASE_CONNECTIONS.labels(database_type=db_type).set(count)
    
    @staticmethod
    async def update_business_metrics():
        """Update business metrics from database."""
        try:
            from app.services.analytics_service import AnalyticsService
            analytics = AnalyticsService()
            
            # Update property metrics
            property_stats = await analytics.get_property_statistics()
            for stat in property_stats:
                PROPERTY_METRICS.labels(
                    status=stat['status'],
                    property_type=stat['property_type']
                ).set(stat['count'])
            
            # Update user metrics
            user_stats = await analytics.get_user_statistics()
            for stat in user_stats:
                USER_METRICS.labels(
                    role=stat['role'],
                    status=stat['status']
                ).set(stat['count'])
                
        except Exception as e:
            logger.error(f"Failed to update business metrics: {e}")


def setup_metrics() -> Instrumentator:
    """Setup Prometheus metrics collection."""
    # Create instrumentator
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_group_untemplated=True,
        should_instrument_requests_inprogress=True,
        should_instrument_requests_size=True,
        should_instrument_response_size=True,
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    
    # Add custom metrics
    @instrumentator.counter(
        "http_requests_custom_total",
        "Total HTTP requests (custom)",
        labels=["method", "endpoint", "status_code"]
    )
    def custom_request_counter(info):
        return {"method": info.method, "endpoint": info.modified_endpoint, "status_code": info.response.status_code}
    
    return instrumentator


def get_metrics() -> str:
    """Get Prometheus metrics in text format."""
    try:
        return generate_latest(REGISTRY).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return ""


# Health check metrics
HEALTH_CHECK_STATUS = Gauge(
    'health_check_status',
    'Health check status (1=healthy, 0=unhealthy)',
    ['service'],
    registry=REGISTRY
)


class HealthChecker:
    """Application health checker."""
    
    @staticmethod
    async def check_database_health() -> bool:
        """Check PostgreSQL database health."""
        try:
            from app.core.database import engine
            if engine:
                async with engine.begin() as conn:
                    await conn.execute(text("SELECT 1"))
                HEALTH_CHECK_STATUS.labels(service="postgresql").set(1)
                return True
            else:
                HEALTH_CHECK_STATUS.labels(service="postgresql").set(0)
                return False
        except Exception:
            HEALTH_CHECK_STATUS.labels(service="postgresql").set(0)
            return False
    
    @staticmethod
    async def check_redis_health() -> bool:
        """Check Redis health."""
        try:
            from app.core.redis import redis_client
            if redis_client:
                # Use ping() method for async redis client
                pong = await redis_client.ping()
                if pong is True:  # async redis returns True instead of "PONG"
                    HEALTH_CHECK_STATUS.labels(service="redis").set(1)
                    return True
            HEALTH_CHECK_STATUS.labels(service="redis").set(0)
            return False
        except Exception as e:
            logger.error(f"Redis health check error: {e}")
            HEALTH_CHECK_STATUS.labels(service="redis").set(0)
            return False
    
    @staticmethod
    async def check_mongodb_health() -> bool:
        """Check MongoDB health."""
        try:
            from app.core.mongodb import mongodb_manager
            is_healthy = await mongodb_manager.health_check()
            HEALTH_CHECK_STATUS.labels(service="mongodb").set(1 if is_healthy else 0)
            return is_healthy
        except Exception:
            HEALTH_CHECK_STATUS.labels(service="mongodb").set(0)
            return False
    
    @staticmethod
    async def check_clickhouse_health() -> bool:
        """Check ClickHouse health."""
        try:
            from app.core.clickhouse import clickhouse_manager
            is_healthy = await clickhouse_manager.health_check()
            HEALTH_CHECK_STATUS.labels(service="clickhouse").set(1 if is_healthy else 0)
            return is_healthy
        except Exception:
            HEALTH_CHECK_STATUS.labels(service="clickhouse").set(0)
            return False
    
    @staticmethod
    async def check_kafka_health() -> bool:
        """Check Kafka health."""
        try:
            from app.core.kafka import kafka_manager
            is_healthy = await kafka_manager.health_check()
            HEALTH_CHECK_STATUS.labels(service="kafka").set(1 if is_healthy else 0)
            return is_healthy
        except Exception:
            HEALTH_CHECK_STATUS.labels(service="kafka").set(0)
            return False
    
    @staticmethod
    async def get_overall_health() -> Dict[str, Any]:
        """Get overall application health status."""
        checks = {
            "postgresql": await HealthChecker.check_database_health(),
            "redis": await HealthChecker.check_redis_health(),
            "mongodb": await HealthChecker.check_mongodb_health(),
            "clickhouse": await HealthChecker.check_clickhouse_health(),
            "kafka": await HealthChecker.check_kafka_health(),
        }
        
        overall_healthy = all(checks.values())
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "checks": checks,
            "timestamp": time.time()
        }
