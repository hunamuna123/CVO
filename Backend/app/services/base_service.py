"""
Base service class with common functionality.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.base import BaseModel

T = TypeVar('T', bound=BaseModel)


class BaseService:
    """
    Base service class providing common database operations.
    
    This class contains common methods that can be inherited by other services
    to avoid code duplication.
    """

    @staticmethod
    async def get_by_id(
        db: AsyncSession, 
        model: Type[T], 
        item_id: str,
        relationships: Optional[List[str]] = None
    ) -> Optional[T]:
        """
        Get a single item by ID.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
            item_id: Item ID
            relationships: List of relationships to load
            
        Returns:
            Model instance or None if not found
        """
        query = select(model).where(model.id == item_id)
        
        if relationships:
            for rel in relationships:
                query = query.options(selectinload(getattr(model, rel)))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        model: Type[T],
        skip: int = 0,
        limit: int = 100,
        relationships: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> List[T]:
        """
        Get multiple items with pagination and filtering.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
            skip: Number of items to skip
            limit: Maximum number of items to return
            relationships: List of relationships to load
            filters: Dictionary of filters to apply
            order_by: Column to order by
            
        Returns:
            List of model instances
        """
        query = select(model)
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(model, key) and value is not None:
                    query = query.where(getattr(model, key) == value)
        
        # Apply ordering
        if order_by:
            if order_by.endswith('_desc'):
                column = order_by[:-5]
                if hasattr(model, column):
                    query = query.order_by(getattr(model, column).desc())
            elif order_by.endswith('_asc'):
                column = order_by[:-4]
                if hasattr(model, column):
                    query = query.order_by(getattr(model, column).asc())
            else:
                if hasattr(model, order_by):
                    query = query.order_by(getattr(model, order_by))
        
        # Apply relationships
        if relationships:
            for rel in relationships:
                if hasattr(model, rel):
                    query = query.options(selectinload(getattr(model, rel)))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def count(
        db: AsyncSession,
        model: Type[T],
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count items with optional filtering.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
            filters: Dictionary of filters to apply
            
        Returns:
            Count of items
        """
        query = select(func.count(model.id))
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(model, key) and value is not None:
                    query = query.where(getattr(model, key) == value)
        
        result = await db.execute(query)
        return result.scalar()

    @staticmethod
    async def create(
        db: AsyncSession,
        model: Type[T],
        **kwargs
    ) -> T:
        """
        Create a new item.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
            **kwargs: Model fields
            
        Returns:
            Created model instance
        """
        instance = model(**kwargs)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def update(
        db: AsyncSession,
        instance: T,
        **kwargs
    ) -> T:
        """
        Update an existing item.
        
        Args:
            db: Database session
            instance: Model instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated model instance
        """
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def delete(
        db: AsyncSession,
        instance: T
    ) -> None:
        """
        Delete an item.
        
        Args:
            db: Database session
            instance: Model instance to delete
        """
        await db.delete(instance)
        await db.commit()

    @staticmethod
    def calculate_pagination(
        total: int,
        page: int,
        limit: int
    ) -> Dict[str, Any]:
        """
        Calculate pagination metadata.
        
        Args:
            total: Total number of items
            page: Current page number
            limit: Items per page
            
        Returns:
            Dictionary with pagination metadata
        """
        pages = math.ceil(total / limit) if total > 0 else 1
        has_next = page < pages
        has_prev = page > 1
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
            "has_next": has_next,
            "has_prev": has_prev,
        }

    @staticmethod
    async def search_by_text(
        db: AsyncSession,
        model: Type[T],
        search_query: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[T], int]:
        """
        Search items by text across multiple fields.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
            search_query: Text to search for
            search_fields: List of fields to search in
            skip: Number of items to skip
            limit: Maximum number of items to return
            additional_filters: Additional filters to apply
            
        Returns:
            Tuple of (items, total_count)
        """
        # Build search conditions
        search_conditions = []
        for field in search_fields:
            if hasattr(model, field):
                search_conditions.append(
                    getattr(model, field).ilike(f"%{search_query}%")
                )
        
        if not search_conditions:
            return [], 0
        
        # Base query with search conditions
        base_query = select(model)
        count_query = select(func.count(model.id))
        
        # Combine search conditions with OR
        from sqlalchemy import or_
        search_filter = or_(*search_conditions)
        
        base_query = base_query.where(search_filter)
        count_query = count_query.where(search_filter)
        
        # Apply additional filters
        if additional_filters:
            for key, value in additional_filters.items():
                if hasattr(model, key) and value is not None:
                    base_query = base_query.where(getattr(model, key) == value)
                    count_query = count_query.where(getattr(model, key) == value)
        
        # Get total count
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get items with pagination
        query = base_query.offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total

    @staticmethod
    def build_sort_clause(model: Type[T], sort_param: str):
        """
        Build sort clause from sort parameter.
        
        Args:
            model: SQLAlchemy model class
            sort_param: Sort parameter (e.g., "name_asc", "created_desc")
            
        Returns:
            SQLAlchemy order_by clause or None
        """
        if not sort_param:
            return None
        
        if sort_param.endswith('_desc'):
            column_name = sort_param[:-5]
            if hasattr(model, column_name):
                return getattr(model, column_name).desc()
        elif sort_param.endswith('_asc'):
            column_name = sort_param[:-4]
            if hasattr(model, column_name):
                return getattr(model, column_name).asc()
        else:
            if hasattr(model, sort_param):
                return getattr(model, sort_param)
        
        # Default to created_at desc if sort is invalid
        if hasattr(model, 'created_at'):
            return model.created_at.desc()
        
        return None

    @staticmethod
    def apply_date_range_filter(
        query,
        model: Type[T],
        date_field: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ):
        """
        Apply date range filter to query.
        
        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model class
            date_field: Name of the date field
            date_from: Start date (YYYY-MM-DD format)
            date_to: End date (YYYY-MM-DD format)
            
        Returns:
            Modified query
        """
        if not hasattr(model, date_field):
            return query
        
        field = getattr(model, date_field)
        
        if date_from:
            try:
                from datetime import datetime
                start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
                query = query.where(field >= start_date)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        if date_to:
            try:
                from datetime import datetime
                end_date = datetime.strptime(date_to, "%Y-%m-%d").date()
                query = query.where(field <= end_date)
            except ValueError:
                pass  # Invalid date format, skip filter
        
        return query

    @staticmethod
    def apply_numeric_range_filter(
        query,
        model: Type[T],
        field_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ):
        """
        Apply numeric range filter to query.
        
        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model class
            field_name: Name of the numeric field
            min_value: Minimum value
            max_value: Maximum value
            
        Returns:
            Modified query
        """
        if not hasattr(model, field_name):
            return query
        
        field = getattr(model, field_name)
        
        if min_value is not None:
            query = query.where(field >= min_value)
        
        if max_value is not None:
            query = query.where(field <= max_value)
        
        return query
