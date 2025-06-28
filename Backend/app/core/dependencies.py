"""
Dependency injection container and service locator.

This module provides a comprehensive dependency injection system for
managing service dependencies and ensuring proper separation of concerns.
"""

from __future__ import annotations

import abc
from typing import TypeVar, Generic, Dict, Type, Any, Callable, Optional
from functools import lru_cache
import asyncio
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import get_settings
from app.models.user import User
from app.utils.security import get_current_user

T = TypeVar('T')


class ServiceContainer:
    """
    Service container for dependency injection.
    
    This container manages service instances and their dependencies,
    providing a clean way to inject services throughout the application.
    """
    
    def __init__(self):
        self._services: Dict[Type[T], Any] = {}
        self._factories: Dict[Type[T], Callable[[], T]] = {}
        self._singletons: Dict[Type[T], Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service."""
        self._singletons[interface] = implementation
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a transient service (new instance each time)."""
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for creating service instances."""
        self._factories[interface] = factory
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance by interface."""
        # Check singletons first
        if interface in self._singletons:
            if not hasattr(self, f'_singleton_{interface.__name__}'):
                instance = self._singletons[interface]()
                setattr(self, f'_singleton_{interface.__name__}', instance)
            return getattr(self, f'_singleton_{interface.__name__}')
        
        # Check factories
        if interface in self._factories:
            return self._factories[interface]()
        
        # Check transient services
        if interface in self._services:
            return self._services[interface]()
        
        raise ValueError(f"Service {interface} not registered")


# Global service container
container = ServiceContainer()


class IUnitOfWork(abc.ABC):
    """Unit of Work interface for database transactions."""
    
    @abc.abstractmethod
    async def __aenter__(self):
        pass
    
    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    @abc.abstractmethod
    async def commit(self) -> None:
        pass
    
    @abc.abstractmethod
    async def rollback(self) -> None:
        pass


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work pattern."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
    
    async def commit(self) -> None:
        await self.db.commit()
    
    async def rollback(self) -> None:
        await self.db.rollback()


class IDatabaseContext(abc.ABC):
    """Database context interface."""
    
    @abc.abstractmethod
    async def get_session(self) -> AsyncSession:
        pass
    
    @abc.abstractmethod
    async def get_unit_of_work(self) -> IUnitOfWork:
        pass


class DatabaseContext(IDatabaseContext):
    """Database context implementation."""
    
    def __init__(self):
        self._session: Optional[AsyncSession] = None
    
    async def get_session(self) -> AsyncSession:
        if not self._session:
            self._session = await get_db().__anext__()
        return self._session
    
    async def get_unit_of_work(self) -> IUnitOfWork:
        session = await self.get_session()
        return SqlAlchemyUnitOfWork(session)


class ICurrentUser(abc.ABC):
    """Current user interface."""
    
    @abc.abstractmethod
    async def get_user(self) -> User:
        pass
    
    @abc.abstractmethod
    async def get_user_id(self) -> str:
        pass
    
    @abc.abstractmethod
    async def is_authenticated(self) -> bool:
        pass
    
    @abc.abstractmethod
    async def has_role(self, role: str) -> bool:
        pass


class CurrentUserContext(ICurrentUser):
    """Current user context implementation."""
    
    def __init__(self, user: Optional[User] = None):
        self._user = user
    
    async def get_user(self) -> User:
        if not self._user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        return self._user
    
    async def get_user_id(self) -> str:
        user = await self.get_user()
        return str(user.id)
    
    async def is_authenticated(self) -> bool:
        return self._user is not None
    
    async def has_role(self, role: str) -> bool:
        if not self._user:
            return False
        return self._user.role.value == role


# Dependency providers
async def get_database_context() -> IDatabaseContext:
    """Get database context dependency."""
    return DatabaseContext()


async def get_current_user_context(
    current_user: User = Depends(get_current_user)
) -> ICurrentUser:
    """Get current user context dependency."""
    return CurrentUserContext(current_user)


async def get_optional_user_context(
    request: Any = None
) -> ICurrentUser:
    """Get optional user context (may be None for anonymous users)."""
    try:
        # Try to get current user, but don't fail if not authenticated
        from app.utils.security import get_current_user_optional
        user = await get_current_user_optional(request)
        return CurrentUserContext(user)
    except:
        return CurrentUserContext(None)


class ServiceBase:
    """Base class for all services with common dependencies."""
    
    def __init__(
        self,
        db_context: IDatabaseContext,
        user_context: Optional[ICurrentUser] = None,
    ):
        self.db_context = db_context
        self.user_context = user_context
    
    async def get_session(self) -> AsyncSession:
        """Get database session."""
        return await self.db_context.get_session()
    
    async def get_unit_of_work(self) -> IUnitOfWork:
        """Get unit of work for transactions."""
        return await self.db_context.get_unit_of_work()
    
    async def get_current_user(self) -> User:
        """Get current authenticated user."""
        if not self.user_context:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        return await self.user_context.get_user()
    
    async def get_current_user_id(self) -> str:
        """Get current user ID."""
        user = await self.get_current_user()
        return str(user.id)


class IServiceFactory(abc.ABC, Generic[T]):
    """Service factory interface."""
    
    @abc.abstractmethod
    async def create(self, **kwargs) -> T:
        pass


class ServiceFactory(IServiceFactory[T]):
    """Generic service factory implementation."""
    
    def __init__(self, service_class: Type[T]):
        self.service_class = service_class
    
    async def create(self, **kwargs) -> T:
        """Create service instance with dependencies."""
        # Inject common dependencies
        if 'db_context' not in kwargs:
            kwargs['db_context'] = DatabaseContext()
        
        return self.service_class(**kwargs)


# Decorators for dependency injection
def inject_dependencies(func: Callable) -> Callable:
    """Decorator to inject dependencies into service methods."""
    
    async def wrapper(*args, **kwargs):
        # Add common dependencies if not present
        if 'db_context' not in kwargs:
            kwargs['db_context'] = DatabaseContext()
        
        return await func(*args, **kwargs)
    
    return wrapper


def with_transaction(func: Callable) -> Callable:
    """Decorator to wrap service method in database transaction."""
    
    async def wrapper(self, *args, **kwargs):
        async with await self.get_unit_of_work() as uow:
            try:
                result = await func(self, *args, **kwargs)
                await uow.commit()
                return result
            except Exception:
                await uow.rollback()
                raise
    
    return wrapper


# Caching decorators
def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache service method results."""
    
    def decorator(func: Callable) -> Callable:
        @lru_cache(maxsize=128)
        async def wrapper(*args, **kwargs):
            # Implementation depends on your caching strategy
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


# Registration of core services
def configure_services() -> None:
    """Configure service registrations."""
    # Only import services when actually configuring to avoid circular imports
    from app.services.user_service import UserService
    from app.services.auth_service import AuthService
    from app.services.property_service import PropertyService
    
    # Register services as singletons
    container.register_singleton(ICurrentUser, CurrentUserContext)
    container.register_singleton(IDatabaseContext, DatabaseContext)
    
    # Register business services as transient
    container.register_transient(UserService, UserService)
    container.register_transient(AuthService, AuthService)
    container.register_transient(PropertyService, PropertyService)


_services_configured = False

def ensure_services_configured() -> None:
    """Ensure services are configured, but only once."""
    global _services_configured
    if not _services_configured:
        configure_services()
        _services_configured = True
