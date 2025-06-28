"""
Property repository implementation.

This module provides property-specific data access operations,
including advanced search and filtering capabilities.
"""

import abc
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.property import Property, PropertyType, DealType, PropertyStatus
from app.repositories.base import BaseRepository, FilterSpec, SortSpec, QueryResult, PaginationSpec


class IPropertyRepository(abc.ABC):
    """Property repository interface."""
    
    @abc.abstractmethod
    async def search_properties(
        self, 
        search_params: Dict[str, Any],
        pagination: Optional[PaginationSpec] = None
    ) -> QueryResult[Property]:
        """Search properties with advanced filtering."""
        pass
    
    @abc.abstractmethod
    async def get_by_developer(self, developer_id: UUID) -> List[Property]:
        """Get all properties by developer."""
        pass
    
    @abc.abstractmethod
    async def get_featured_properties(self, limit: int = 10) -> List[Property]:
        """Get featured properties."""
        pass
    
    @abc.abstractmethod
    async def get_properties_by_price_range(
        self, 
        min_price: Decimal, 
        max_price: Decimal
    ) -> List[Property]:
        """Get properties within price range."""
        pass
    
    @abc.abstractmethod
    async def get_properties_by_location(
        self, 
        city: str, 
        district: Optional[str] = None
    ) -> List[Property]:
        """Get properties by location."""
        pass
    
    @abc.abstractmethod
    async def get_similar_properties(
        self, 
        property_id: UUID, 
        limit: int = 5
    ) -> List[Property]:
        """Get similar properties based on criteria."""
        pass
    
    @abc.abstractmethod
    async def update_view_count(self, property_id: UUID) -> bool:
        """Increment property view count."""
        pass


class PropertyRepository(BaseRepository[Property], IPropertyRepository):
    """Property repository implementation."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Property)
    
    async def search_properties(
        self, 
        search_params: Dict[str, Any],
        pagination: Optional[PaginationSpec] = None
    ) -> QueryResult[Property]:
        """Search properties with advanced filtering."""
        filters = []
        
        # Property type filter
        if "property_type" in search_params:
            filters.append(FilterSpec("property_type", "eq", search_params["property_type"]))
        
        # Deal type filter
        if "deal_type" in search_params:
            filters.append(FilterSpec("deal_type", "eq", search_params["deal_type"]))
        
        # Price range filter
        if "price_min" in search_params:
            filters.append(FilterSpec("price", "gte", search_params["price_min"]))
        if "price_max" in search_params:
            filters.append(FilterSpec("price", "lte", search_params["price_max"]))
        
        # Location filters
        if "city" in search_params:
            filters.append(FilterSpec("city", "eq", search_params["city"]))
        if "district" in search_params:
            filters.append(FilterSpec("district", "eq", search_params["district"]))
        
        # Area filters
        if "total_area_min" in search_params:
            filters.append(FilterSpec("total_area", "gte", search_params["total_area_min"]))
        if "total_area_max" in search_params:
            filters.append(FilterSpec("total_area", "lte", search_params["total_area_max"]))
        
        # Rooms filter
        if "rooms_count" in search_params:
            if isinstance(search_params["rooms_count"], list):
                filters.append(FilterSpec("rooms_count", "in", search_params["rooms_count"]))
            else:
                filters.append(FilterSpec("rooms_count", "eq", search_params["rooms_count"]))
        
        # Features filters
        if search_params.get("has_parking"):
            filters.append(FilterSpec("has_parking", "eq", True))
        if search_params.get("has_balcony"):
            filters.append(FilterSpec("has_balcony", "eq", True))
        if search_params.get("has_elevator"):
            filters.append(FilterSpec("has_elevator", "eq", True))
        
        # Status filter (default to active)
        status_filter = search_params.get("status", PropertyStatus.ACTIVE)
        filters.append(FilterSpec("status", "eq", status_filter))
        
        # Sorting
        sort_by = search_params.get("sort", "created_desc")
        sorts = []
        
        if sort_by == "price_asc":
            sorts.append(SortSpec("price", "asc"))
        elif sort_by == "price_desc":
            sorts.append(SortSpec("price", "desc"))
        elif sort_by == "area_asc":
            sorts.append(SortSpec("total_area", "asc"))
        elif sort_by == "area_desc":
            sorts.append(SortSpec("total_area", "desc"))
        elif sort_by == "created_desc":
            sorts.append(SortSpec("created_at", "desc"))
        else:
            sorts.append(SortSpec("created_at", "desc"))
        
        return await self.get_all(
            filters=filters,
            sorts=sorts,
            pagination=pagination
        )
    
    async def get_by_developer(self, developer_id: UUID) -> List[Property]:
        """Get all properties by developer."""
        return await self.get_many_by_field("developer_id", developer_id)
    
    async def get_featured_properties(self, limit: int = 10) -> List[Property]:
        """Get featured properties."""
        filters = [
            FilterSpec("is_featured", "eq", True),
            FilterSpec("status", "eq", PropertyStatus.ACTIVE)
        ]
        
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("created_at", "desc")],
            limit=limit
        )
    
    async def get_properties_by_price_range(
        self, 
        min_price: Decimal, 
        max_price: Decimal
    ) -> List[Property]:
        """Get properties within price range."""
        filters = [
            FilterSpec("price", "gte", min_price),
            FilterSpec("price", "lte", max_price),
            FilterSpec("status", "eq", PropertyStatus.ACTIVE)
        ]
        
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("price", "asc")]
        )
    
    async def get_properties_by_location(
        self, 
        city: str, 
        district: Optional[str] = None
    ) -> List[Property]:
        """Get properties by location."""
        filters = [
            FilterSpec("city", "eq", city),
            FilterSpec("status", "eq", PropertyStatus.ACTIVE)
        ]
        
        if district:
            filters.append(FilterSpec("district", "eq", district))
        
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("created_at", "desc")]
        )
    
    async def get_similar_properties(
        self, 
        property_id: UUID, 
        limit: int = 5
    ) -> List[Property]:
        """Get similar properties based on criteria."""
        # First, get the reference property
        reference_property = await self.get_by_id(property_id)
        if not reference_property:
            return []
        
        # Find similar properties based on type, deal type, and price range
        price_tolerance = reference_property.price * Decimal("0.2")  # 20% tolerance
        min_price = reference_property.price - price_tolerance
        max_price = reference_property.price + price_tolerance
        
        filters = [
            FilterSpec("property_type", "eq", reference_property.property_type),
            FilterSpec("deal_type", "eq", reference_property.deal_type),
            FilterSpec("city", "eq", reference_property.city),
            FilterSpec("price", "gte", min_price),
            FilterSpec("price", "lte", max_price),
            FilterSpec("status", "eq", PropertyStatus.ACTIVE),
            FilterSpec("id", "ne", property_id)  # Exclude the reference property
        ]
        
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("created_at", "desc")],
            limit=limit
        )
    
    async def update_view_count(self, property_id: UUID) -> bool:
        """Increment property view count."""
        query = select(Property).where(Property.id == property_id)
        result = await self.db.execute(query)
        property_obj = result.scalar_one_or_none()
        
        if property_obj:
            property_obj.views_count += 1
            await self.db.flush()
            return True
        
        return False
    
    async def get_property_with_images(self, property_id: UUID) -> Optional[Property]:
        """Get property with all images."""
        query = select(Property).options(
            selectinload(Property.images),
            selectinload(Property.documents),
            joinedload(Property.developer)
        ).where(Property.id == property_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_properties_statistics(self) -> Dict[str, Any]:
        """Get property statistics."""
        # Total properties
        total_query = select(func.count(Property.id))
        total_result = await self.db.execute(total_query)
        total_properties = total_result.scalar()
        
        # Properties by status
        status_query = select(Property.status, func.count(Property.id)).group_by(Property.status)
        status_result = await self.db.execute(status_query)
        properties_by_status = {status.value: count for status, count in status_result.all()}
        
        # Properties by type
        type_query = select(Property.property_type, func.count(Property.id)).group_by(Property.property_type)
        type_result = await self.db.execute(type_query)
        properties_by_type = {prop_type.value: count for prop_type, count in type_result.all()}
        
        # Average price
        avg_price_query = select(func.avg(Property.price)).where(Property.status == PropertyStatus.ACTIVE)
        avg_price_result = await self.db.execute(avg_price_query)
        average_price = avg_price_result.scalar() or 0
        
        return {
            "total_properties": total_properties,
            "properties_by_status": properties_by_status,
            "properties_by_type": properties_by_type,
            "average_price": float(average_price)
        }
    
    async def get_popular_properties(self, limit: int = 10) -> List[Property]:
        """Get most viewed properties."""
        filters = [FilterSpec("status", "eq", PropertyStatus.ACTIVE)]
        sorts = [SortSpec("views_count", "desc")]
        
        return await self.find_many(
            filters=filters,
            sorts=sorts,
            limit=limit
        )
    
    async def get_properties_by_price_per_sqm_range(
        self, 
        min_price_per_sqm: Decimal, 
        max_price_per_sqm: Decimal
    ) -> List[Property]:
        """Get properties by price per square meter range."""
        filters = [
            FilterSpec("price_per_sqm", "gte", min_price_per_sqm),
            FilterSpec("price_per_sqm", "lte", max_price_per_sqm),
            FilterSpec("status", "eq", PropertyStatus.ACTIVE)
        ]
        
        return await self.find_many(
            filters=filters,
            sorts=[SortSpec("price_per_sqm", "asc")]
        )
