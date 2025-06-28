"""
Database connection and session management.
"""

import asyncio
import time
from typing import AsyncGenerator, Optional

import structlog
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

# Global variables for database connection
engine: Optional[AsyncEngine] = None
async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


def create_engine() -> AsyncEngine:
    """
    Create and configure the database engine.
    """
    settings = get_settings()
    engine_kwargs = {
        "echo": settings.debug,
        "echo_pool": settings.debug,
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
        "pool_pre_ping": True,
        "pool_recycle": 300,  # 5 minutes
    }

    # Use NullPool for testing to avoid connection issues
    if settings.is_testing:
        engine_kwargs["poolclass"] = NullPool

    return create_async_engine(settings.get_database_url(), **engine_kwargs)


async def create_db_connection() -> None:
    """
    Create database connection and session maker.
    """
    global engine, async_session_maker

    try:
        engine = create_engine()
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        # Test the connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("Database connection established successfully")

    except Exception as e:
        logger.error("Failed to create database connection", error=str(e))
        raise


async def close_db_connection() -> None:
    """
    Close database connection.
    """
    global engine

    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    """
    if not async_session_maker:
        raise RuntimeError("Database not initialized")

    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.
    """
    async for session in get_async_session():
        yield session


# Event listeners for database monitoring will be set up after engine creation
def setup_database_listeners(engine: AsyncEngine) -> None:
    """Set up database event listeners."""
    from sqlalchemy.pool import Pool

    @event.listens_for(Pool, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragma for foreign key support (if using SQLite)."""
        if "sqlite" in str(dbapi_connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def receive_before_cursor_execute(
        conn, cursor, statement, parameters, context, executemany
    ):
        """Log SQL queries in debug mode."""
        settings = get_settings()
        if settings.debug:
            logger.debug(
                "Executing SQL",
                statement=statement[:100] + "..."
                if len(statement) > 100
                else statement,
                parameter_count=len(parameters) if parameters else 0,
            )


# Database utilities
async def create_tables() -> None:
    """
    Create all database tables.
    """
    if not engine:
        raise RuntimeError("Database engine not initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables created")


async def drop_tables() -> None:
    """
    Drop all database tables.
    """
    if not engine:
        raise RuntimeError("Database engine not initialized")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.info("Database tables dropped")


async def reset_database() -> None:
    """
    Reset database (drop and create all tables).
    Warning: This will delete all data!
    """
    await drop_tables()
    await create_tables()
    logger.info("Database reset completed")


class DatabaseManager:
    """
    Database manager for handling connections and transactions.
    """

    def __init__(self):
        self.engine = engine
        self.session_maker = async_session_maker

    async def execute_query(self, query: str, parameters: Optional[dict] = None) -> any:
        """
        Execute a raw SQL query.
        """
        async with self.get_session() as session:
            result = await session.execute(text(query), parameters or {})
            await session.commit()
            return result

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session.
        """
        async for session in get_async_session():
            yield session

    async def health_check(self) -> bool:
        """
        Check database health.
        """
        try:
            async with self.get_session() as session:
                await session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return False


# Create a global database manager instance
db_manager = DatabaseManager()
