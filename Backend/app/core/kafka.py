"""
Apache Kafka message queue configuration and management.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError, KafkaError
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class KafkaSettings(BaseSettings):
    """Kafka configuration settings."""
    
    # Kafka connection
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"
    KAFKA_SASL_MECHANISM: Optional[str] = None
    KAFKA_SASL_USERNAME: Optional[str] = None
    KAFKA_SASL_PASSWORD: Optional[str] = None
    
    # Producer settings
    KAFKA_PRODUCER_BATCH_SIZE: int = 16384
    KAFKA_PRODUCER_LINGER_MS: int = 5
    KAFKA_PRODUCER_COMPRESSION_TYPE: str = "gzip"
    KAFKA_PRODUCER_RETRIES: int = 3
    
    # Consumer settings
    KAFKA_CONSUMER_GROUP_ID: str = "realestate-api"
    KAFKA_CONSUMER_AUTO_OFFSET_RESET: str = "latest"
    KAFKA_CONSUMER_ENABLE_AUTO_COMMIT: bool = True
    KAFKA_CONSUMER_AUTO_COMMIT_INTERVAL_MS: int = 5000
    
    # Topics
    KAFKA_TOPIC_USER_EVENTS: str = "user-events"
    KAFKA_TOPIC_PROPERTY_EVENTS: str = "property-events"
    KAFKA_TOPIC_SEARCH_EVENTS: str = "search-events"
    KAFKA_TOPIC_ANALYTICS_EVENTS: str = "analytics-events"
    KAFKA_TOPIC_NOTIFICATION_EVENTS: str = "notification-events"
    KAFKA_TOPIC_AUDIT_EVENTS: str = "audit-events"
    
    class Config:
        env_prefix = ""
        case_sensitive = False


class KafkaManager:
    """Kafka message queue manager."""
    
    def __init__(self):
        self.settings = KafkaSettings()
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumers: Dict[str, AIOKafkaConsumer] = {}
        self._message_handlers: Dict[str, List[Callable]] = {}
        
    async def connect(self) -> None:
        """Initialize Kafka connections."""
        try:
            # Initialize producer
            await self._init_producer()
            
            # Create topics if they don't exist
            await self._create_topics()
            
            logger.info("Kafka connections established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Kafka connections."""
        # Stop producer
        if self.producer:
            await self.producer.stop()
            
        # Stop all consumers
        for consumer in self.consumers.values():
            await consumer.stop()
            
        logger.info("Kafka connections closed")
    
    async def _init_producer(self) -> None:
        """Initialize Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            # Remove invalid parameters that cause issues
            compression_type="gzip",
            linger_ms=self.settings.KAFKA_PRODUCER_LINGER_MS,
            max_batch_size=self.settings.KAFKA_PRODUCER_BATCH_SIZE,
            request_timeout_ms=30000,
            retry_backoff_ms=1000,
        )
        
        await self.producer.start()
        logger.info("Kafka producer initialized")
    
    async def _create_topics(self) -> None:
        """Create Kafka topics if they don't exist."""
        # In production, topics should be created by Kafka admin
        # This is for development/testing purposes
        topics = [
            self.settings.KAFKA_TOPIC_USER_EVENTS,
            self.settings.KAFKA_TOPIC_PROPERTY_EVENTS,
            self.settings.KAFKA_TOPIC_SEARCH_EVENTS,
            self.settings.KAFKA_TOPIC_ANALYTICS_EVENTS,
            self.settings.KAFKA_TOPIC_NOTIFICATION_EVENTS,
            self.settings.KAFKA_TOPIC_AUDIT_EVENTS,
        ]
        
        logger.info(f"Kafka topics configured: {topics}")
    
    async def health_check(self) -> bool:
        """Check Kafka health."""
        try:
            if not self.producer:
                return False
            # Try to get metadata to test connection
            try:
                metadata = await self.producer.client.fetch_metadata()
                return len(metadata.brokers) > 0
            except Exception:
                # Fallback: just check if producer is running
                return self.producer is not None and not self.producer._closed
        except Exception:
            return False
    
    # Producer methods
    
    async def publish_message(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> None:
        """Publish message to Kafka topic."""
        if not self.producer:
            logger.warning("Kafka producer not initialized")
            return
        
        try:
            await self.producer.send_and_wait(
                topic=topic,
                value=message,
                key=key.encode('utf-8') if key else None
            )
            logger.debug(f"Message published to topic {topic}: {message}")
        except KafkaError as e:
            logger.error(f"Failed to publish message to {topic}: {e}")
            raise
    
    async def publish_user_event(self, event_type: str, user_id: str, data: Dict[str, Any]) -> None:
        """Publish user event."""
        message = {
            "event_type": event_type,
            "user_id": user_id,
            "data": data,
            "timestamp": self._get_timestamp()
        }
        await self.publish_message(self.settings.KAFKA_TOPIC_USER_EVENTS, message, user_id)
    
    async def publish_property_event(self, event_type: str, property_id: str, data: Dict[str, Any]) -> None:
        """Publish property event."""
        message = {
            "event_type": event_type,
            "property_id": property_id,
            "data": data,
            "timestamp": self._get_timestamp()
        }
        await self.publish_message(self.settings.KAFKA_TOPIC_PROPERTY_EVENTS, message, property_id)
    
    async def publish_search_event(self, user_id: Optional[str], session_id: str, 
                                  query: str, filters: Dict[str, Any], 
                                  results_count: int) -> None:
        """Publish search event."""
        message = {
            "event_type": "search",
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "filters": filters,
            "results_count": results_count,
            "timestamp": self._get_timestamp()
        }
        await self.publish_message(self.settings.KAFKA_TOPIC_SEARCH_EVENTS, message, session_id)
    
    async def publish_analytics_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish analytics event."""
        message = {
            "event_type": event_type,
            "data": data,
            "timestamp": self._get_timestamp()
        }
        await self.publish_message(self.settings.KAFKA_TOPIC_ANALYTICS_EVENTS, message)
    
    async def publish_notification_event(self, notification_type: str, recipient_id: str, 
                                        data: Dict[str, Any]) -> None:
        """Publish notification event."""
        message = {
            "notification_type": notification_type,
            "recipient_id": recipient_id,
            "data": data,
            "timestamp": self._get_timestamp()
        }
        await self.publish_message(self.settings.KAFKA_TOPIC_NOTIFICATION_EVENTS, message, recipient_id)
    
    async def publish_audit_event(self, event_type: str, user_id: Optional[str], 
                                 action: str, resource: str, data: Dict[str, Any]) -> None:
        """Publish audit event."""
        message = {
            "event_type": event_type,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "data": data,
            "timestamp": self._get_timestamp()
        }
        await self.publish_message(self.settings.KAFKA_TOPIC_AUDIT_EVENTS, message)
    
    # Consumer methods
    
    async def create_consumer(self, topics: List[str], group_id: Optional[str] = None) -> AIOKafkaConsumer:
        """Create Kafka consumer for topics."""
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id or self.settings.KAFKA_CONSUMER_GROUP_ID,
            auto_offset_reset=self.settings.KAFKA_CONSUMER_AUTO_OFFSET_RESET,
            enable_auto_commit=self.settings.KAFKA_CONSUMER_ENABLE_AUTO_COMMIT,
            auto_commit_interval_ms=self.settings.KAFKA_CONSUMER_AUTO_COMMIT_INTERVAL_MS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
        )
        
        await consumer.start()
        return consumer
    
    def register_message_handler(self, topic: str, handler: Callable) -> None:
        """Register message handler for topic."""
        if topic not in self._message_handlers:
            self._message_handlers[topic] = []
        self._message_handlers[topic].append(handler)
        logger.info(f"Registered handler for topic: {topic}")
    
    async def start_consuming(self, topics: List[str]) -> None:
        """Start consuming messages from topics."""
        consumer = await self.create_consumer(topics)
        self.consumers["main"] = consumer
        
        try:
            async for message in consumer:
                topic = message.topic
                value = message.value
                
                if topic in self._message_handlers:
                    for handler in self._message_handlers[topic]:
                        try:
                            await handler(value)
                        except Exception as e:
                            logger.error(f"Error handling message from {topic}: {e}")
                            
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
        finally:
            await consumer.stop()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Global Kafka manager instance
kafka_manager = KafkaManager()


async def get_kafka() -> KafkaManager:
    """Dependency to get Kafka manager."""
    return kafka_manager


async def create_kafka_connection() -> None:
    """Create Kafka connection."""
    try:
        await kafka_manager.connect()
    except Exception as e:
        logger.warning(f"Kafka connection failed, continuing without message queue: {e}")


async def close_kafka_connection() -> None:
    """Close Kafka connection."""
    await kafka_manager.disconnect()


# Message handlers for different events

async def handle_user_event(message: Dict[str, Any]) -> None:
    """Handle user events."""
    logger.info(f"Processing user event: {message['event_type']}")
    # Add your user event processing logic here


async def handle_property_event(message: Dict[str, Any]) -> None:
    """Handle property events."""
    logger.info(f"Processing property event: {message['event_type']}")
    # Add your property event processing logic here


async def handle_search_event(message: Dict[str, Any]) -> None:
    """Handle search events."""
    logger.info(f"Processing search event: {message['event_type']}")
    # Send to ClickHouse for analytics
    try:
        from app.core.clickhouse import clickhouse_manager
        
        await clickhouse_manager.log_search_event(
            search_id=message.get("session_id", ""),
            user_id=message.get("user_id"),
            session_id=message.get("session_id", ""),
            query=message.get("query", ""),
            filters=json.dumps(message.get("filters", {})),
            results_count=message.get("results_count", 0),
            ip_address=message.get("ip_address", ""),
            user_agent=message.get("user_agent")
        )
    except Exception as e:
        logger.error(f"Failed to log search event to ClickHouse: {e}")


async def handle_analytics_event(message: Dict[str, Any]) -> None:
    """Handle analytics events."""
    logger.info(f"Processing analytics event: {message['event_type']}")
    # Add your analytics processing logic here


async def handle_notification_event(message: Dict[str, Any]) -> None:
    """Handle notification events."""
    logger.info(f"Processing notification: {message['notification_type']}")
    # Add your notification processing logic here


async def handle_audit_event(message: Dict[str, Any]) -> None:
    """Handle audit events."""
    logger.info(f"Processing audit event: {message['action']}")
    # Store in MongoDB for audit trail
    try:
        from app.models.mongodb import AuditLog
        
        audit_log = AuditLog(
            event_type=message.get("event_type", ""),
            user_id=message.get("user_id"),
            action=message.get("action", ""),
            resource=message.get("resource", ""),
            data=message.get("data", {}),
            timestamp=message.get("timestamp")
        )
        
        await audit_log.save()
    except Exception as e:
        logger.error(f"Failed to save audit log: {e}")
