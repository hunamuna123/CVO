"""
Base repository implementation with common CRUD operations.

This module provides the foundation for all repository implementations,
ensuring consistent data access patterns across the application.
"""

import abc
from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from uuid import UUID

from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.sql import Select

from app.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class FilterSpec:
    """Specification for database filtering."""
    
    def __init__(self, field: str, operator: str, value: Any):
        self.field = field
        self.operator = operator
        self.value = value
    
    def apply(self, query: Select, model: Type[T]) -> Select:
        """Apply filter to SQLAlchemy query."""
        column = getattr(model, self.field)
        
        if self.operator == 'eq':
            return query.where(column == self.value)
        elif self.operator == 'ne':
            return query.where(column != self.value)
        elif self.operator == 'gt':
            return query.where(column > self.value)
        elif self.operator == 'gte':
            return query.where(column >= self.value)
        elif self.operator == 'lt':
            return query.where(column < self.value)
        elif self.operator == 'lte':
            return query.where(column <= self.value)
        elif self.operator == 'like':
            return query.where(column.like(f"%{self.value}%"))
        elif self.operator == 'ilike':
            return query.where(column.ilike(f"%{self.value}%"))
        elif self.operator == 'in':
            return query.where(column.in_(self.value))
        elif self.operator == 'not_in':
            return query.where(~column.in_(self.value))
        elif self.operator == 'is_null':
            return query.where(column.is_(None))
        elif self.operator == 'is_not_null':
            return query.where(column.is_not(None))
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")


class SortSpec:
    """Specification for database sorting."""
    
    def __init__(self, field: str, direction: str = 'asc'):
        self.field = field
        self.direction = direction.lower()
    
    def apply(self, query: Select, model: Type[T]) -> Select:
        """Apply sorting to SQLAlchemy query."""
        column = getattr(model, self.field)
        
        if self.direction == 'desc':
            return query.order_by(column.desc())
        else:
            return query.order_by(column.asc())


class PaginationSpec:
    """Specification for database pagination."""
    
    def __init__(self, page: int = 1, page_size: int = 20):
        self.page = max(1, page)
        self.page_size = min(max(1, page_size), 100)  # Max 100 items per page
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size
    
    def apply(self, query: Select) -> Select:
        """Apply pagination to SQLAlchemy query."""
        return query.offset(self.offset).limit(self.page_size)


class QueryResult(Generic[T]):
    """Result wrapper for paginated queries."""
    
    def __init__(
        self,
        items: List[T],
        total_count: int,
        page: int,
        page_size: int,
        has_next: bool = False,
        has_previous: bool = False
    ):
        self.items = items
        self.total_count = total_count
        self.page = page
        self.page_size = page_size
        self.has_next = has_next
        self.has_previous = has_previous
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total_count + self.page_size - 1) // self.page_size


class IRepository(abc.ABC, Generic[T]):
    """Abstract repository interface."""
    
    @abc.abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abc.abstractmethod
    async def get_all(
        self,
        filters: Optional[List[FilterSpec]] = None,
        sorts: Optional[List[SortSpec]] = None,
        pagination: Optional[PaginationSpec] = None
    ) -> QueryResult[T]:
        """Get all entities with optional filtering, sorting, and pagination."""
        pass
    
    @abc.abstractmethod
    async def create(self, entity: T) -> T:
        """Create new entity."""
        pass
    
    @abc.abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity."""
        pass
    
    @abc.abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        pass
    
    @abc.abstractmethod
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists by ID."""
        pass
    
    @abc.abstractmethod
    async def count(self, filters: Optional[List[FilterSpec]] = None) -> int:
        """Count entities with optional filtering."""
        pass


class BaseRepository(IRepository[T]):
    """Base repository implementation with common CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get entity by ID."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get entity by specific field."""
        column = getattr(self.model, field)
        query = select(self.model).where(column == value)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_many_by_field(self, field: str, value: Any) -> List[T]:
        """Get multiple entities by specific field."""
        column = getattr(self.model, field)
        query = select(self.model).where(column == value)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(
        self,
        filters: Optional[List[FilterSpec]] = None,
        sorts: Optional[List[SortSpec]] = None,
        pagination: Optional[PaginationSpec] = None
    ) -> QueryResult[T]:
        """Get all entities with optional filtering, sorting, and pagination."""
        
        # Build base query
        query = select(self.model)
        
        # Apply filters
        if filters:
            for filter_spec in filters:
                query = filter_spec.apply(query, self.model)
        
        # Get total count before pagination
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply sorting
        if sorts:
            for sort_spec in sorts:
                query = sort_spec.apply(query, self.model)
        else:
            # Default sorting by creation date
            query = query.order_by(self.model.created_at.desc())
        
        # Apply pagination
        pagination = pagination or PaginationSpec()
        query = pagination.apply(query)
        
        # Execute query
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        
        # Calculate pagination info
        has_next = (pagination.offset + len(items)) < total_count
        has_previous = pagination.page > 1
        
        return QueryResult(
            items=items,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            has_next=has_next,
            has_previous=has_previous
        )
    
    async def create(self, entity: T) -> T:
        """Create new entity."""
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    
    async def create_many(self, entities: List[T]) -> List[T]:
        """Create multiple entities."""
        self.db.add_all(entities)
        await self.db.flush()
        for entity in entities:
            await self.db.refresh(entity)
        return entities
    
    async def update(self, entity: T) -> T:
        """Update existing entity."""
        await self.db.merge(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
    
    async def update_by_id(self, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID with partial data."""
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        query = delete(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    async def delete_many(self, ids: List[UUID]) -> int:
        """Delete multiple entities by IDs."""
        query = delete(self.model).where(self.model.id.in_(ids))
        result = await self.db.execute(query)
        return result.rowcount
    
    async def exists(self, id: UUID) -> bool:
        """Check if entity exists by ID."""
        query = select(func.count()).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def exists_by_field(self, field: str, value: Any) -> bool:
        """Check if entity exists by specific field."""
        column = getattr(self.model, field)
        query = select(func.count()).where(column == value)
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def count(self, filters: Optional[List[FilterSpec]] = None) -> int:
        """Count entities with optional filtering."""
        query = select(func.count()).select_from(self.model)
        
        if filters:
            for filter_spec in filters:
                query = filter_spec.apply(query, self.model)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def find_one(self, filters: List[FilterSpec]) -> Optional[T]:
        """Find single entity by filters."""
        query = select(self.model)
        
        for filter_spec in filters:
            query = filter_spec.apply(query, self.model)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def find_many(
        self,
        filters: List[FilterSpec],
        sorts: Optional[List[SortSpec]] = None,
        limit: Optional[int] = None
    ) -> List[T]:
        """Find multiple entities by filters."""
        query = select(self.model)
        
        for filter_spec in filters:
            query = filter_spec.apply(query, self.model)
        
        if sorts:
            for sort_spec in sorts:
                query = sort_spec.apply(query, self.model)
        
        if limit:
            query = query.limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    def with_relations(self, *relations) -> 'BaseRepository[T]':
        """Include relations in queries (for eager loading)."""
        # This would modify the base query to include relations
        # Implementation depends on specific use case
        return self
