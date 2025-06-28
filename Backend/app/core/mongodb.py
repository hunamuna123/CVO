"""
MongoDB configuration and connection management using Motor and Beanie.
"""

import logging
from typing import List, Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MongoDBSettings(BaseSettings):
    """MongoDB configuration settings."""
    
    # MongoDB connection
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "realestate_documents"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    
    # Collections configuration
    MONGODB_LOGS_COLLECTION: str = "application_logs"
    MONGODB_AUDIT_COLLECTION: str = "audit_logs"
    MONGODB_DOCUMENTS_COLLECTION: str = "property_documents"
    MONGODB_ANALYTICS_COLLECTION: str = "user_analytics"
    
    class Config:
        env_prefix = "MONGODB_"


class MongoDBManager:
    """MongoDB connection and operations manager."""
    
    def __init__(self):
        self.settings = MongoDBSettings()
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        
    async def connect(self) -> None:
        """Create MongoDB connection."""
        try:
            self.client = AsyncIOMotorClient(
                self.settings.MONGODB_URL,
                minPoolSize=self.settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=self.settings.MONGODB_MAX_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Get database
            self.database = self.client[self.settings.MONGODB_DATABASE]
            
            # Initialize Beanie with document models
            await self._init_beanie()
            
            logger.info("MongoDB connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def _init_beanie(self) -> None:
        """Initialize Beanie ODM with document models."""
        from app.models.mongodb import (
            ApplicationLog,
            AuditLog,
            PropertyDocument,
            UserAnalytics,
        )
        
        await init_beanie(
            database=self.database,
            document_models=[
                ApplicationLog,
                AuditLog,
                PropertyDocument,
                UserAnalytics,
            ]
        )
        
        logger.info("Beanie ODM initialized successfully")
    
    async def health_check(self) -> bool:
        """Check MongoDB health."""
        try:
            if not self.client:
                return False
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def get_collection(self, collection_name: str):
        """Get MongoDB collection."""
        if not self.database:
            raise RuntimeError("MongoDB not connected")
        return self.database[collection_name]


# Global MongoDB manager instance
mongodb_manager = MongoDBManager()


async def get_mongodb() -> MongoDBManager:
    """Dependency to get MongoDB manager."""
    return mongodb_manager


async def create_mongodb_connection() -> None:
    """Create MongoDB connection."""
    await mongodb_manager.connect()


async def close_mongodb_connection() -> None:
    """Close MongoDB connection."""
    await mongodb_manager.disconnect()
