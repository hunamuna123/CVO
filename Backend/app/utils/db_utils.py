"""
Database utilities to prevent async/sync context issues.

This module provides utilities to safely handle database operations
and prevent MissingGreenlet errors when accessing lazy-loaded attributes.
"""

import asyncio
import functools
from typing import Any, Callable, List, Optional, TypeVar, Union

import structlog
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.base import instance_state

logger = structlog.get_logger(__name__)

T = TypeVar('T')


def ensure_async_context():
    """
    Decorator to ensure function is running in async context.
    
    Raises RuntimeError if called from synchronous context.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Check if we're in an event loop
                loop = asyncio.get_running_loop()
                if loop is None:
                    raise RuntimeError("Function must be called in async context")
                return await func(*args, **kwargs)
            except RuntimeError as e:
                if "no running event loop" in str(e):
                    raise RuntimeError(f"Function {func.__name__} must be called in async context")
                raise
        return wrapper
    return decorator


async def safe_refresh_object(db: AsyncSession, obj: Any, attribute_names: Optional[List[str]] = None) -> None:
    """
    Safely refresh an SQLAlchemy object to avoid lazy loading issues.
    
    Args:
        db: Database session
        obj: SQLAlchemy model instance
        attribute_names: Specific attributes to refresh, or None for all
    """
    try:
        if attribute_names:
            await db.refresh(obj, attribute_names)
        else:
            await db.refresh(obj)
    except Exception as e:
        logger.warning(
            "Failed to refresh object",
            object_type=type(obj).__name__,
            object_id=getattr(obj, 'id', 'unknown'),
            error=str(e),
        )
        # Don't raise - allow operation to continue


async def safe_access_attribute(db: AsyncSession, obj: Any, attr_name: str, default: Any = None) -> Any:
    """
    Safely access an attribute that might require lazy loading.
    
    Args:
        db: Database session
        obj: SQLAlchemy model instance
        attr_name: Name of the attribute to access
        default: Default value if attribute cannot be accessed
        
    Returns:
        Attribute value or default
    """
    try:
        # Check if attribute is already loaded
        state = instance_state(obj)
        if state and hasattr(state, 'attrs'):
            attr_state = state.attrs.get(attr_name)
            if attr_state and attr_state.loaded_value is not None:
                # Attribute is already loaded, safe to access
                return getattr(obj, attr_name, default)
        
        # Attribute might need loading - refresh object first
        await safe_refresh_object(db, obj)
        return getattr(obj, attr_name, default)
        
    except Exception as e:
        logger.warning(
            "Failed to safely access attribute",
            object_type=type(obj).__name__,
            attribute=attr_name,
            error=str(e),
        )
        return default


def get_unloaded_relationships(obj: Any) -> List[str]:
    """
    Get list of unloaded relationship attributes for an SQLAlchemy object.
    
    Args:
        obj: SQLAlchemy model instance
        
    Returns:
        List of unloaded relationship attribute names
    """
    unloaded = []
    inspector = inspect(obj.__class__)
    
    for relationship in inspector.relationships:
        try:
            state = instance_state(obj)
            if state and hasattr(state, 'attrs'):
                attr_state = state.attrs.get(relationship.key)
                if attr_state and not attr_state.loaded_value:
                    unloaded.append(relationship.key)
        except Exception:
            # If we can't determine state, assume it might be unloaded
            unloaded.append(relationship.key)
    
    return unloaded


async def preload_relationships(db: AsyncSession, obj: Any, relationship_names: Optional[List[str]] = None) -> None:
    """
    Preload specific relationships for an SQLAlchemy object.
    
    Args:
        db: Database session
        obj: SQLAlchemy model instance
        relationship_names: Specific relationships to load, or None for all unloaded ones
    """
    try:
        if relationship_names is None:
            relationship_names = get_unloaded_relationships(obj)
        
        if relationship_names:
            await db.refresh(obj, relationship_names)
            
    except Exception as e:
        logger.warning(
            "Failed to preload relationships",
            object_type=type(obj).__name__,
            relationships=relationship_names,
            error=str(e),
        )


def safe_attribute_access(default: Any = None):
    """
    Decorator for methods that access potentially lazy-loaded attributes.
    
    This decorator ensures the method is async and provides safe attribute access.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, db: AsyncSession, obj: Any, *args, **kwargs):
            # Ensure object is fresh and relationships are loaded
            await safe_refresh_object(db, obj)
            
            try:
                return await func(self, db, obj, *args, **kwargs)
            except Exception as e:
                logger.error(
                    "Error in safe attribute access",
                    function=func.__name__,
                    object_type=type(obj).__name__,
                    error=str(e),
                    exc_info=True,
                )
                if default is not None:
                    return default
                raise
                
        return wrapper
    return decorator


class DatabaseContextManager:
    """
    Context manager to ensure proper database session handling.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._objects_to_refresh: List[Any] = []
    
    def track_object(self, obj: Any) -> None:
        """Track an object for automatic refresh on context exit."""
        if obj not in self._objects_to_refresh:
            self._objects_to_refresh.append(obj)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Refresh all tracked objects to ensure they're in a consistent state
        for obj in self._objects_to_refresh:
            await safe_refresh_object(self.db, obj)


async def ensure_object_fresh(db: AsyncSession, obj: Any, relationships: Optional[List[str]] = None) -> Any:
    """
    Ensure an SQLAlchemy object is fresh and has required relationships loaded.
    
    Args:
        db: Database session
        obj: SQLAlchemy model instance
        relationships: List of relationship names to ensure are loaded
        
    Returns:
        The refreshed object
    """
    try:
        # First, refresh the object itself
        await db.refresh(obj)
        
        # Then, load specific relationships if requested
        if relationships:
            await preload_relationships(db, obj, relationships)
        
        return obj
        
    except Exception as e:
        logger.error(
            "Failed to ensure object freshness",
            object_type=type(obj).__name__,
            object_id=getattr(obj, 'id', 'unknown'),
            relationships=relationships,
            error=str(e),
            exc_info=True,
        )
        # Return object as-is if refresh fails
        return obj


def create_safe_accessor(attribute_name: str, default_value: Any = None):
    """
    Create a safe accessor function for a potentially lazy-loaded attribute.
    
    Args:
        attribute_name: Name of the attribute to access
        default_value: Default value if attribute cannot be accessed
        
    Returns:
        Async function that safely accesses the attribute
    """
    async def safe_accessor(db: AsyncSession, obj: Any) -> Any:
        return await safe_access_attribute(db, obj, attribute_name, default_value)
    
    return safe_accessor


# Common safe accessors for frequently used attributes
safe_get_created_at = create_safe_accessor('created_at')
safe_get_updated_at = create_safe_accessor('updated_at')
safe_get_id = create_safe_accessor('id')


async def validate_database_state(db: AsyncSession) -> bool:
    """
    Validate that the database session is in a good state.
    
    Args:
        db: Database session to validate
        
    Returns:
        True if session is valid, False otherwise
    """
    try:
        # Try a simple query to test the connection
        await db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(
            "Database session validation failed",
            error=str(e),
            exc_info=True,
        )
        return False


class SafeModelAccess:
    """
    Utility class for safe model attribute access.
    """
    
    @staticmethod
    async def get_timestamp_fields(db: AsyncSession, obj: Any) -> dict:
        """
        Safely get created_at and updated_at fields from a model.
        
        Args:
            db: Database session
            obj: SQLAlchemy model instance
            
        Returns:
            Dict with created_at and updated_at values
        """
        try:
            await db.refresh(obj)
            return {
                'created_at': getattr(obj, 'created_at', None),
                'updated_at': getattr(obj, 'updated_at', None),
            }
        except Exception as e:
            logger.warning(
                "Failed to get timestamp fields",
                object_type=type(obj).__name__,
                error=str(e),
            )
            return {'created_at': None, 'updated_at': None}
    
    @staticmethod
    async def get_relationship_safely(db: AsyncSession, obj: Any, relationship_name: str) -> Any:
        """
        Safely get a relationship attribute from a model.
        
        Args:
            db: Database session
            obj: SQLAlchemy model instance
            relationship_name: Name of the relationship to access
            
        Returns:
            Relationship object or None if not accessible
        """
        try:
            # Try to load the relationship
            await db.refresh(obj, [relationship_name])
            return getattr(obj, relationship_name, None)
        except Exception as e:
            logger.warning(
                "Failed to get relationship",
                object_type=type(obj).__name__,
                relationship=relationship_name,
                error=str(e),
            )
            return None
