"""
Complex service for business logic related to residential complexes.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Complex, Developer
from app.schemas.complex import (
    ComplexCreateRequest,
    ComplexListResponse,
    ComplexResponse,
    ComplexSearchParams,
    ComplexSearchResponse,
    ComplexUpdateRequest,
)
from app.services.base_service import BaseService


class ComplexService(BaseService):
    """Service for complex-related operations."""

    async def search_complexes(
        self, db: AsyncSession, params: ComplexSearchParams
    ) -> ComplexSearchResponse:
        """
        Search complexes with advanced filtering and pagination.
        
        Args:
            db: Database session
            params: Search parameters
            
        Returns:
            Search response with paginated results
        """
        # Build base query
        query = select(Complex).options(
            selectinload(Complex.developer),
            selectinload(Complex.complex_images)
        )
        
        count_query = select(Complex.id)
        
        # Apply filters
        if params.complex_class:
            query = query.where(Complex.complex_class == params.complex_class)
            count_query = count_query.where(Complex.complex_class == params.complex_class)
        
        if params.status:
            query = query.where(Complex.status == params.status)
            count_query = count_query.where(Complex.status == params.status)
        
        if params.region:
            query = query.where(Complex.region.ilike(f"%{params.region}%"))
            count_query = count_query.where(Complex.region.ilike(f"%{params.region}%"))
        
        if params.city:
            query = query.where(Complex.city.ilike(f"%{params.city}%"))
            count_query = count_query.where(Complex.city.ilike(f"%{params.city}%"))
        
        if params.district:
            query = query.where(Complex.district.ilike(f"%{params.district}%"))
            count_query = count_query.where(Complex.district.ilike(f"%{params.district}%"))
        
        # Price filters
        if params.price_from is not None:
            query = query.where(Complex.price_from >= params.price_from)
            count_query = count_query.where(Complex.price_from >= params.price_from)
        
        if params.price_to is not None:
            query = query.where(Complex.price_to <= params.price_to)
            count_query = count_query.where(Complex.price_to <= params.price_to)
        
        # Developer filters
        if params.developer_id:
            query = query.where(Complex.developer_id == params.developer_id)
            count_query = count_query.where(Complex.developer_id == params.developer_id)
        
        if params.developer_verified is not None:
            query = query.join(Developer).where(Developer.is_verified == params.developer_verified)
            count_query = count_query.join(Developer).where(Developer.is_verified == params.developer_verified)
        
        if params.is_featured is not None:
            query = query.where(Complex.is_featured == params.is_featured)
            count_query = count_query.where(Complex.is_featured == params.is_featured)
        
        # Infrastructure filters
        if params.has_parking is not None:
            query = query.where(Complex.has_parking == params.has_parking)
            count_query = count_query.where(Complex.has_parking == params.has_parking)
        
        if params.has_playground is not None:
            query = query.where(Complex.has_playground == params.has_playground)
            count_query = count_query.where(Complex.has_playground == params.has_playground)
        
        if params.has_school is not None:
            query = query.where(Complex.has_school == params.has_school)
            count_query = count_query.where(Complex.has_school == params.has_school)
        
        if params.has_kindergarten is not None:
            query = query.where(Complex.has_kindergarten == params.has_kindergarten)
            count_query = count_query.where(Complex.has_kindergarten == params.has_kindergarten)
        
        if params.has_shopping_center is not None:
            query = query.where(Complex.has_shopping_center == params.has_shopping_center)
            count_query = count_query.where(Complex.has_shopping_center == params.has_shopping_center)
        
        if params.has_fitness_center is not None:
            query = query.where(Complex.has_fitness_center == params.has_fitness_center)
            count_query = count_query.where(Complex.has_fitness_center == params.has_fitness_center)
        
        # Text search
        if params.search:
            search_filter = (
                Complex.name.ilike(f"%{params.search}%") |
                Complex.description.ilike(f"%{params.search}%") |
                Complex.address.ilike(f"%{params.search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Geographic search
        if params.lat and params.lng and params.radius:
            # Simplified distance calculation (for production, use PostGIS)
            lat_range = params.radius / 111.0  # Rough km to degree conversion
            lng_range = params.radius / (111.0 * abs(params.lat / 90.0))
            
            geo_filter = (
                (Complex.latitude.between(params.lat - lat_range, params.lat + lat_range)) &
                (Complex.longitude.between(params.lng - lng_range, params.lng + lng_range))
            )
            query = query.where(geo_filter)
            count_query = count_query.where(geo_filter)
        
        # Date filters (construction and completion years)
        if params.construction_year_from:
            from sqlalchemy import extract
            query = query.where(extract('year', Complex.construction_start_date) >= params.construction_year_from)
            count_query = count_query.where(extract('year', Complex.construction_start_date) >= params.construction_year_from)
        
        if params.construction_year_to:
            from sqlalchemy import extract
            query = query.where(extract('year', Complex.construction_start_date) <= params.construction_year_to)
            count_query = count_query.where(extract('year', Complex.construction_start_date) <= params.construction_year_to)
        
        if params.completion_year_from:
            from sqlalchemy import extract
            query = query.where(extract('year', Complex.planned_completion_date) >= params.completion_year_from)
            count_query = count_query.where(extract('year', Complex.planned_completion_date) >= params.completion_year_from)
        
        if params.completion_year_to:
            from sqlalchemy import extract
            query = query.where(extract('year', Complex.planned_completion_date) <= params.completion_year_to)
            count_query = count_query.where(extract('year', Complex.planned_completion_date) <= params.completion_year_to)
        
        # Get total count
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Apply sorting
        sort_clause = self.build_sort_clause(Complex, params.sort)
        if sort_clause is not None:
            query = query.order_by(sort_clause)
        
        # Apply pagination
        skip = (params.page - 1) * params.limit
        query = query.offset(skip).limit(params.limit)
        
        # Execute query
        result = await db.execute(query)
        complexes = result.scalars().all()
        
        # Convert to response format
        items = []
        for complex_obj in complexes:
            # Calculate properties count (placeholder)
            properties_count = len(complex_obj.properties) if hasattr(complex_obj, 'properties') else 0
            
            item = ComplexListResponse(
                id=str(complex_obj.id),
                name=complex_obj.name,
                complex_class=complex_obj.complex_class,
                status=complex_obj.status,
                region=complex_obj.region,
                city=complex_obj.city,
                district=complex_obj.district,
                full_address=complex_obj.full_address,
                price_from=complex_obj.price_from,
                price_to=complex_obj.price_to,
                has_parking=complex_obj.has_parking,
                has_playground=complex_obj.has_playground,
                has_school=complex_obj.has_school,
                has_kindergarten=complex_obj.has_kindergarten,
                main_image_url=complex_obj.main_image_url,
                developer=complex_obj.developer,
                properties_count=properties_count,
                completion_progress=complex_obj.completion_progress,
                construction_start_date=complex_obj.construction_start_date,
                planned_completion_date=complex_obj.planned_completion_date,
                created_at=complex_obj.created_at.isoformat(),
            )
            items.append(item)
        
        # Calculate pagination
        pagination = self.calculate_pagination(total, params.page, params.limit)
        
        return ComplexSearchResponse(
            items=items,
            **pagination,
            filters_applied={
                "complex_class": params.complex_class,
                "status": params.status,
                "region": params.region,
                "city": params.city,
                "developer_verified": params.developer_verified,
                "is_featured": params.is_featured,
            },
            sort_applied=params.sort,
            search_query=params.search,
        )

    async def get_featured_complexes(
        self, db: AsyncSession, limit: int
    ) -> List[ComplexListResponse]:
        """
        Get featured complexes.
        
        Args:
            db: Database session
            limit: Maximum number of complexes to return
            
        Returns:
            List of featured complexes
        """
        query = select(Complex).options(
            selectinload(Complex.developer)
        ).where(
            Complex.is_featured == True
        ).order_by(
            Complex.created_at.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        complexes = result.scalars().all()
        
        items = []
        for complex_obj in complexes:
            properties_count = len(complex_obj.properties) if hasattr(complex_obj, 'properties') else 0
            
            item = ComplexListResponse(
                id=str(complex_obj.id),
                name=complex_obj.name,
                complex_class=complex_obj.complex_class,
                status=complex_obj.status,
                region=complex_obj.region,
                city=complex_obj.city,
                district=complex_obj.district,
                full_address=complex_obj.full_address,
                price_from=complex_obj.price_from,
                price_to=complex_obj.price_to,
                has_parking=complex_obj.has_parking,
                has_playground=complex_obj.has_playground,
                has_school=complex_obj.has_school,
                has_kindergarten=complex_obj.has_kindergarten,
                main_image_url=complex_obj.main_image_url,
                developer=complex_obj.developer,
                properties_count=properties_count,
                completion_progress=complex_obj.completion_progress,
                construction_start_date=complex_obj.construction_start_date,
                planned_completion_date=complex_obj.planned_completion_date,
                created_at=complex_obj.created_at.isoformat(),
            )
            items.append(item)
        
        return items

    async def get_complex_by_id(
        self, db: AsyncSession, complex_id: str
    ) -> ComplexResponse:
        """
        Get complex by ID with full details.
        
        Args:
            db: Database session
            complex_id: Complex UUID
            
        Returns:
            Complex details
            
        Raises:
            HTTPException: If complex not found
        """
        query = select(Complex).options(
            selectinload(Complex.developer),
            selectinload(Complex.complex_images),
            selectinload(Complex.properties)
        ).where(Complex.id == complex_id)
        
        result = await db.execute(query)
        complex_obj = result.scalar_one_or_none()
        
        if not complex_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "COMPLEX_NOT_FOUND",
                        "message": "Жилой комплекс не найден",
                        "details": {"complex_id": complex_id},
                    }
                },
            )
        
        properties_count = len(complex_obj.properties) if complex_obj.properties else 0
        
        return ComplexResponse(
            id=str(complex_obj.id),
            name=complex_obj.name,
            description=complex_obj.description,
            complex_class=complex_obj.complex_class,
            status=complex_obj.status,
            region=complex_obj.region,
            city=complex_obj.city,
            district=complex_obj.district,
            full_address=complex_obj.full_address,
            latitude=complex_obj.latitude,
            longitude=complex_obj.longitude,
            total_buildings=complex_obj.total_buildings,
            total_apartments=complex_obj.total_apartments,
            price_from=complex_obj.price_from,
            price_to=complex_obj.price_to,
            has_parking=complex_obj.has_parking,
            has_playground=complex_obj.has_playground,
            has_school=complex_obj.has_school,
            has_kindergarten=complex_obj.has_kindergarten,
            has_shopping_center=complex_obj.has_shopping_center,
            has_fitness_center=complex_obj.has_fitness_center,
            has_concierge=complex_obj.has_concierge,
            has_security=complex_obj.has_security,
            is_featured=complex_obj.is_featured,
            main_image_url=complex_obj.main_image_url,
            logo_url=complex_obj.logo_url,
            virtual_tour_url=complex_obj.virtual_tour_url,
            website_url=complex_obj.website_url,
            images=[],  # Placeholder for images
            developer=complex_obj.developer,
            properties_count=properties_count,
            completion_progress=complex_obj.completion_progress,
            construction_start_date=complex_obj.construction_start_date,
            planned_completion_date=complex_obj.planned_completion_date,
            actual_completion_date=complex_obj.actual_completion_date,
            created_at=complex_obj.created_at.isoformat(),
            updated_at=complex_obj.updated_at.isoformat(),
        )

    async def create_complex(
        self, db: AsyncSession, complex_data: ComplexCreateRequest, developer_id: str
    ) -> ComplexResponse:
        """
        Create a new complex.
        
        Args:
            db: Database session
            complex_data: Complex creation data
            developer_id: Developer ID
            
        Returns:
            Created complex
        """
        # Verify developer exists and is verified
        developer = await self.get_by_id(db, Developer, developer_id)
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "DEVELOPER_NOT_FOUND",
                        "message": "Застройщик не найден",
                        "details": {},
                    }
                },
            )
        
        if not developer.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "DEVELOPER_NOT_VERIFIED",
                        "message": "Только верифицированные застройщики могут создавать комплексы",
                        "details": {},
                    }
                },
            )
        
        # Create complex
        complex_obj = Complex(
            developer_id=developer_id,
            **complex_data.model_dump()
        )
        
        db.add(complex_obj)
        await db.commit()
        await db.refresh(complex_obj)
        
        # Load relationships
        await db.refresh(complex_obj, ["developer"])
        
        return ComplexResponse(
            id=str(complex_obj.id),
            name=complex_obj.name,
            description=complex_obj.description,
            complex_class=complex_obj.complex_class,
            status=complex_obj.status,
            region=complex_obj.region,
            city=complex_obj.city,
            district=complex_obj.district,
            full_address=complex_obj.full_address,
            latitude=complex_obj.latitude,
            longitude=complex_obj.longitude,
            total_buildings=complex_obj.total_buildings,
            total_apartments=complex_obj.total_apartments,
            price_from=complex_obj.price_from,
            price_to=complex_obj.price_to,
            has_parking=complex_obj.has_parking,
            has_playground=complex_obj.has_playground,
            has_school=complex_obj.has_school,
            has_kindergarten=complex_obj.has_kindergarten,
            has_shopping_center=complex_obj.has_shopping_center,
            has_fitness_center=complex_obj.has_fitness_center,
            has_concierge=complex_obj.has_concierge,
            has_security=complex_obj.has_security,
            is_featured=complex_obj.is_featured,
            main_image_url=complex_obj.main_image_url,
            logo_url=complex_obj.logo_url,
            virtual_tour_url=complex_obj.virtual_tour_url,
            website_url=complex_obj.website_url,
            images=[],
            developer=complex_obj.developer,
            properties_count=0,
            completion_progress=complex_obj.completion_progress,
            construction_start_date=complex_obj.construction_start_date,
            planned_completion_date=complex_obj.planned_completion_date,
            actual_completion_date=complex_obj.actual_completion_date,
            created_at=complex_obj.created_at.isoformat(),
            updated_at=complex_obj.updated_at.isoformat(),
        )

    async def update_complex(
        self, db: AsyncSession, complex_id: str, complex_data: ComplexUpdateRequest, developer_id: str
    ) -> ComplexResponse:
        """Update complex (placeholder implementation)."""
        # This would contain the full update logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"error": {"code": "NOT_IMPLEMENTED", "message": "Функция обновления будет реализована позже"}}
        )

    async def delete_complex(
        self, db: AsyncSession, complex_id: str, developer_id: str
    ) -> None:
        """Delete complex (placeholder implementation)."""
        # This would contain the full delete logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"error": {"code": "NOT_IMPLEMENTED", "message": "Функция удаления будет реализована позже"}}
        )

    async def upload_complex_images(
        self, db: AsyncSession, complex_id: str, files, developer_id: str, titles_list
    ) -> list:
        """Upload complex images (placeholder implementation)."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"error": {"code": "NOT_IMPLEMENTED", "message": "Загрузка изображений будет реализована позже"}}
        )

    async def get_complex_properties(
        self, db: AsyncSession, complex_id: str, page: int, limit: int, property_type, status
    ) -> list:
        """Get complex properties (placeholder implementation)."""
        return []

    async def get_complex_analytics(
        self, db: AsyncSession, complex_id: str, developer_id: str, days: int
    ) -> dict:
        """Get complex analytics (placeholder implementation)."""
        return {
            "message": "Аналитика комплекса будет реализована позже",
            "complex_id": complex_id,
            "days": days,
        }
