"""
ClickHouse configuration and connection management for analytics.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from clickhouse_driver import Client
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class ClickHouseSettings(BaseSettings):
    """ClickHouse configuration settings."""
    
    # ClickHouse connection
    CLICKHOUSE_ENABLED: bool = False
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_DATABASE: str = "realestate_analytics"
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_SECURE: bool = False
    
    # Performance settings
    CLICKHOUSE_CONNECT_TIMEOUT: int = 10
    CLICKHOUSE_SEND_RECEIVE_TIMEOUT: int = 300
    CLICKHOUSE_SYNC_REQUEST_TIMEOUT: int = 5
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class ClickHouseManager:
    """ClickHouse connection and operations manager."""
    
    def __init__(self):
        self.settings = ClickHouseSettings()
        self.client: Optional[Client] = None
        
    async def connect(self) -> None:
        """Create ClickHouse connection."""
        try:
            self.client = Client(
                host=self.settings.CLICKHOUSE_HOST,
                port=self.settings.CLICKHOUSE_PORT,
                database=self.settings.CLICKHOUSE_DATABASE,
                user=self.settings.CLICKHOUSE_USER,
                password=self.settings.CLICKHOUSE_PASSWORD,
                secure=self.settings.CLICKHOUSE_SECURE,
                connect_timeout=self.settings.CLICKHOUSE_CONNECT_TIMEOUT,
                send_receive_timeout=self.settings.CLICKHOUSE_SEND_RECEIVE_TIMEOUT,
                sync_request_timeout=self.settings.CLICKHOUSE_SYNC_REQUEST_TIMEOUT,
            )
            
            # Test connection
            result = self.client.execute('SELECT 1')
            if result[0][0] != 1:
                raise Exception("ClickHouse connection test failed")
            
            # Create analytics tables if not exist
            await self._create_analytics_tables()
            
            logger.info("ClickHouse connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close ClickHouse connection."""
        if self.client:
            self.client.disconnect()
            logger.info("ClickHouse connection closed")
    
    async def _create_analytics_tables(self) -> None:
        """Create analytics tables if they don't exist."""
        
        # Property views analytics
        property_views_sql = """
        CREATE TABLE IF NOT EXISTS property_views (
            property_id String,
            user_id Nullable(String),
            session_id String,
            ip_address String,
            user_agent Nullable(String),
            country Nullable(String),
            city Nullable(String),
            device_type Nullable(String),
            referrer Nullable(String),
            timestamp DateTime64(3),
            date Date MATERIALIZED toDate(timestamp)
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(date)
        ORDER BY (property_id, timestamp)
        SETTINGS index_granularity = 8192
        """
        
        # Search analytics
        search_analytics_sql = """
        CREATE TABLE IF NOT EXISTS search_analytics (
            search_id String,
            user_id Nullable(String),
            session_id String,
            query String,
            filters String,
            results_count UInt32,
            ip_address String,
            user_agent Nullable(String),
            timestamp DateTime64(3),
            date Date MATERIALIZED toDate(timestamp)
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(date)
        ORDER BY (timestamp, user_id)
        SETTINGS index_granularity = 8192
        """
        
        # User behavior analytics
        user_behavior_sql = """
        CREATE TABLE IF NOT EXISTS user_behavior (
            user_id Nullable(String),
            session_id String,
            event_type String,
            event_data String,
            page_url String,
            ip_address String,
            user_agent Nullable(String),
            timestamp DateTime64(3),
            date Date MATERIALIZED toDate(timestamp)
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(date)
        ORDER BY (timestamp, session_id)
        SETTINGS index_granularity = 8192
        """
        
        # API performance metrics
        api_metrics_sql = """
        CREATE TABLE IF NOT EXISTS api_metrics (
            endpoint String,
            method String,
            status_code UInt16,
            response_time_ms Float64,
            user_id Nullable(String),
            ip_address String,
            user_agent Nullable(String),
            timestamp DateTime64(3),
            date Date MATERIALIZED toDate(timestamp)
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(date)
        ORDER BY (endpoint, timestamp)
        SETTINGS index_granularity = 8192
        """
        
        # Property price analytics
        price_analytics_sql = """
        CREATE TABLE IF NOT EXISTS price_analytics (
            property_id String,
            price Decimal64(2),
            price_per_sqm Nullable(Decimal64(2)),
            property_type String,
            deal_type String,
            city String,
            district Nullable(String),
            total_area Nullable(Float64),
            rooms_count Nullable(UInt8),
            timestamp DateTime64(3),
            date Date MATERIALIZED toDate(timestamp)
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(date)
        ORDER BY (city, property_type, timestamp)
        SETTINGS index_granularity = 8192
        """
        
        tables = [
            property_views_sql,
            search_analytics_sql,
            user_behavior_sql,
            api_metrics_sql,
            price_analytics_sql,
        ]
        
        for table_sql in tables:
            try:
                self.client.execute(table_sql)
            except Exception as e:
                logger.warning(f"Failed to create ClickHouse table: {e}")
        
        logger.info("ClickHouse analytics tables created successfully")
    
    async def health_check(self) -> bool:
        """Check ClickHouse health."""
        try:
            if not self.client:
                return False
            result = self.client.execute('SELECT 1')
            return result[0][0] == 1
        except Exception:
            return False
    
    # Analytics methods
    
    async def log_property_view(self, 
                               property_id: str,
                               user_id: Optional[str],
                               session_id: str,
                               ip_address: str,
                               user_agent: Optional[str] = None,
                               country: Optional[str] = None,
                               city: Optional[str] = None,
                               device_type: Optional[str] = None,
                               referrer: Optional[str] = None) -> None:
        """Log property view event."""
        if not self.client:
            return
        
        try:
            self.client.execute(
                "INSERT INTO property_views VALUES",
                [{
                    'property_id': property_id,
                    'user_id': user_id,
                    'session_id': session_id,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'country': country,
                    'city': city,
                    'device_type': device_type,
                    'referrer': referrer,
                    'timestamp': datetime.now()
                }]
            )
        except Exception as e:
            logger.error(f"Failed to log property view: {e}")
    
    async def log_search_event(self,
                              search_id: str,
                              user_id: Optional[str],
                              session_id: str,
                              query: str,
                              filters: str,
                              results_count: int,
                              ip_address: str,
                              user_agent: Optional[str] = None) -> None:
        """Log search event."""
        if not self.client:
            return
        
        try:
            self.client.execute(
                "INSERT INTO search_analytics VALUES",
                [{
                    'search_id': search_id,
                    'user_id': user_id,
                    'session_id': session_id,
                    'query': query,
                    'filters': filters,
                    'results_count': results_count,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'timestamp': datetime.now()
                }]
            )
        except Exception as e:
            logger.error(f"Failed to log search event: {e}")
    
    async def log_user_behavior(self,
                               user_id: Optional[str],
                               session_id: str,
                               event_type: str,
                               event_data: str,
                               page_url: str,
                               ip_address: str,
                               user_agent: Optional[str] = None) -> None:
        """Log user behavior event."""
        if not self.client:
            return
        
        try:
            self.client.execute(
                "INSERT INTO user_behavior VALUES",
                [{
                    'user_id': user_id,
                    'session_id': session_id,
                    'event_type': event_type,
                    'event_data': event_data,
                    'page_url': page_url,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'timestamp': datetime.now()
                }]
            )
        except Exception as e:
            logger.error(f"Failed to log user behavior: {e}")
    
    async def log_api_metric(self,
                            endpoint: str,
                            method: str,
                            status_code: int,
                            response_time_ms: float,
                            user_id: Optional[str],
                            ip_address: str,
                            user_agent: Optional[str] = None) -> None:
        """Log API performance metric."""
        if not self.client:
            return
        
        try:
            self.client.execute(
                "INSERT INTO api_metrics VALUES",
                [{
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': status_code,
                    'response_time_ms': response_time_ms,
                    'user_id': user_id,
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'timestamp': datetime.now()
                }]
            )
        except Exception as e:
            logger.error(f"Failed to log API metric: {e}")
    
    async def get_popular_properties(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most viewed properties."""
        if not self.client:
            return []
        
        try:
            query = """
            SELECT 
                property_id,
                count() as views_count,
                uniq(session_id) as unique_visitors
            FROM property_views 
            WHERE date >= today() - INTERVAL %s DAY
            GROUP BY property_id
            ORDER BY views_count DESC
            LIMIT %s
            """
            
            result = self.client.execute(query, [days, limit])
            return [
                {
                    'property_id': row[0],
                    'views_count': row[1],
                    'unique_visitors': row[2]
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Failed to get popular properties: {e}")
            return []
    
    async def get_search_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get popular search queries."""
        if not self.client:
            return []
        
        try:
            query = """
            SELECT 
                query,
                count() as search_count,
                avg(results_count) as avg_results
            FROM search_analytics 
            WHERE date >= today() - INTERVAL %s DAY
            AND query != ''
            GROUP BY query
            ORDER BY search_count DESC
            LIMIT 20
            """
            
            result = self.client.execute(query, [days])
            return [
                {
                    'query': row[0],
                    'search_count': row[1],
                    'avg_results': row[2]
                }
                for row in result
            ]
        except Exception as e:
            logger.error(f"Failed to get search trends: {e}")
            return []


# Global ClickHouse manager instance
clickhouse_manager = ClickHouseManager()


async def get_clickhouse() -> ClickHouseManager:
    """Dependency to get ClickHouse manager."""
    return clickhouse_manager


async def create_clickhouse_connection() -> None:
    """Create ClickHouse connection."""
    settings = ClickHouseSettings()
    if not settings.CLICKHOUSE_ENABLED:
        logger.info("ClickHouse is disabled in configuration")
        return
        
    try:
        await clickhouse_manager.connect()
    except Exception as e:
        logger.warning(f"ClickHouse connection failed, continuing without analytics: {e}")


async def close_clickhouse_connection() -> None:
    """Close ClickHouse connection."""
    await clickhouse_manager.disconnect()
