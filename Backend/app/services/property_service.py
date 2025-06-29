"""
Property service for property management and search functionality.
"""

import time
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

import structlog
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_, desc, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models import Developer, Property, PropertyDocument, PropertyImage, User
from app.models.property import PropertyStatus, PropertyType
from app.schemas.property import (
    PropertyCreateRequest,
    PropertyListResponse,
    PropertyResponse,
    PropertySearchParams,
    PropertySearchResponse,
    PropertyUpdateRequest,
)
from app.services.file_service import FileService

logger = structlog.get_logger(__name__)


class PropertyService:
    """Service for property management and search operations."""

    def __init__(self):
        self.settings = get_settings()
        self.file_service = FileService()

    async def create_property(
        self, db: AsyncSession, property_data: PropertyCreateRequest, developer_id: str
    ) -> PropertyResponse:
        """Create a new property."""
        try:
            # Verify developer exists and is verified
            developer = await self._get_verified_developer(db, developer_id)

            # Create property
            property_dict = property_data.model_dump()
            property_dict["developer_id"] = developer_id
            property_dict["status"] = PropertyStatus.DRAFT

            # Calculate price per sqm if total_area is provided
            if property_dict.get("total_area"):
                property_dict["price_per_sqm"] = property_dict["price"] / Decimal(
                    str(property_dict["total_area"])
                )

            db_property = Property(**property_dict)
            db.add(db_property)
            await db.commit()
            await db.refresh(db_property)

            logger.info(
                "Property created successfully",
                property_id=str(db_property.id),
                developer_id=developer_id,
                title=db_property.title,
            )

            return await self._property_to_response(db, db_property)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to create property",
                developer_id=developer_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PROPERTY_CREATION_FAILED",
                        "message": "Не удалось создать объект недвижимости",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def get_property_by_id(
        self, db: AsyncSession, property_id: str, increment_views: bool = True
    ) -> PropertyResponse:
        """Get property by ID with optional view tracking."""
        try:
            # Get property with all related data
            query = (
                select(Property)
                .options(
                    selectinload(Property.images),
                    selectinload(Property.documents),
                    selectinload(Property.developer).selectinload(Developer.user),
                )
                .where(Property.id == property_id)
            )

            result = await db.execute(query)
            db_property = result.scalar_one_or_none()

            if not db_property:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "PROPERTY_NOT_FOUND",
                            "message": "Объект недвижимости не найден",
                            "details": {},
                        }
                    },
                )

            # Increment view count if requested
            if increment_views:
                db_property.increment_views()
                await db.commit()
                # Refresh to avoid stale data issues
                await db.refresh(db_property)

            return await self._property_to_response(db, db_property)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to get property",
                property_id=property_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PROPERTY_RETRIEVAL_FAILED",
                        "message": "Не удалось получить информацию об объекте",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def update_property(
        self,
        db: AsyncSession,
        property_id: str,
        property_data: PropertyUpdateRequest,
        developer_id: str,
    ) -> PropertyResponse:
        """Update property."""
        try:
            # Get property and verify ownership
            db_property = await self._get_property_by_developer(
                db, property_id, developer_id
            )

            # Update fields
            update_data = property_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_property, field, value)

            # Recalculate price per sqm if needed
            if "total_area" in update_data or "price" in update_data:
                if db_property.total_area and db_property.total_area > 0:
                    db_property.price_per_sqm = db_property.price / Decimal(
                        str(db_property.total_area)
                    )

            await db.commit()
            await db.refresh(db_property)

            logger.info(
                "Property updated successfully",
                property_id=property_id,
                developer_id=developer_id,
            )

            return await self._property_to_response(db, db_property)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to update property",
                property_id=property_id,
                developer_id=developer_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PROPERTY_UPDATE_FAILED",
                        "message": "Не удалось обновить объект недвижимости",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def delete_property(
        self, db: AsyncSession, property_id: str, developer_id: str
    ) -> bool:
        """Delete property."""
        try:
            # Get property and verify ownership
            db_property = await self._get_property_by_developer(
                db, property_id, developer_id
            )

            # Delete associated files
            for image in db_property.images:
                await self.file_service.delete_file(image.url)

            for document in db_property.documents:
                await self.file_service.delete_file(document.file_url)

            # Delete property
            await db.delete(db_property)
            await db.commit()

            logger.info(
                "Property deleted successfully",
                property_id=property_id,
                developer_id=developer_id,
            )

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to delete property",
                property_id=property_id,
                developer_id=developer_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PROPERTY_DELETION_FAILED",
                        "message": "Не удалось удалить объект недвижимости",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def search_properties(
        self, db: AsyncSession, search_params: PropertySearchParams
    ) -> PropertySearchResponse:
        """Search properties with filters and pagination."""
        start_time = time.time()

        try:
            # Build base query
            query = (
                select(Property)
                .options(
                    selectinload(Property.images),
                    selectinload(Property.developer).selectinload(Developer.user),
                )
                .where(Property.status == PropertyStatus.ACTIVE)
            )

            # Apply filters
            filters_applied = {}
            query = self._apply_search_filters(query, search_params, filters_applied)

            # Get total count
            count_query = select(func.count(Property.id)).where(
                Property.status == PropertyStatus.ACTIVE
            )
            count_query = self._apply_search_filters(count_query, search_params, {})
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # Apply sorting
            query = self._apply_sorting(query, search_params.sort)

            # Apply pagination
            offset = (search_params.page - 1) * search_params.limit
            query = query.offset(offset).limit(search_params.limit)

            # Execute query
            result = await db.execute(query)
            properties = result.scalars().all()

            # Convert to response format
            items = []
            for property_obj in properties:
                response_data = await self._property_to_list_response(db, property_obj)
                items.append(response_data)

            # Calculate pagination
            pages = (total + search_params.limit - 1) // search_params.limit
            search_time_ms = (time.time() - start_time) * 1000

            logger.info(
                "Property search completed",
                total_results=total,
                search_time_ms=search_time_ms,
                filters=filters_applied,
            )

            # Calculate pagination metadata
            has_next = search_params.page < pages
            has_prev = search_params.page > 1
            
            from app.schemas.property import PaginationMeta
            pagination = PaginationMeta(
                page=search_params.page,
                limit=search_params.limit,
                total=total,
                pages=pages,
                has_next=has_next,
                has_prev=has_prev,
                next_page=search_params.page + 1 if has_next else None,
                prev_page=search_params.page - 1 if has_prev else None
            )
            
            return PropertySearchResponse(
                items=items,
                pagination=pagination,
                search_time_ms=search_time_ms,
                filters_applied=filters_applied,
                search_query=search_params.search,
            )

        except Exception as e:
            logger.error(
                "Property search failed",
                search_params=search_params.model_dump(),
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "SEARCH_FAILED",
                        "message": "Ошибка при поиске объектов недвижимости",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def get_all_properties(
        self, db: AsyncSession
    ) -> List[PropertyListResponse]:
        """
        Get all active properties without pagination.
        
        Simple method to retrieve all active properties for UI components
        like maps, select lists, or other components that need the full list.
        """
        try:
            # Get all active properties with basic info
            query = (
                select(Property)
                .options(
                    selectinload(Property.images),
                    selectinload(Property.developer).selectinload(Developer.user),
                )
                .where(Property.status == PropertyStatus.ACTIVE)
                .order_by(Property.created_at.desc())
            )
            
            result = await db.execute(query)
            properties = result.scalars().all()
            
            # Convert to response format
            items = []
            for property_obj in properties:
                response_data = await self._property_to_list_response(db, property_obj)
                items.append(response_data)
            
            logger.info("Retrieved all properties", count=len(items))
            return items
            
        except Exception as e:
            logger.error(
                "Failed to get all properties",
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "ALL_PROPERTIES_RETRIEVAL_FAILED",
                        "message": "Не удалось получить список всех объектов",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def get_featured_properties(
        self, db: AsyncSession, limit: int = 10
    ) -> List[PropertyListResponse]:
        """Get featured properties."""
        try:
            query = (
                select(Property)
                .options(
                    selectinload(Property.images),
                    selectinload(Property.developer).selectinload(Developer.user),
                )
                .where(
                    and_(
                        Property.status == PropertyStatus.ACTIVE,
                        Property.is_featured == True,
                    )
                )
                .order_by(desc(Property.created_at))
                .limit(limit)
            )

            result = await db.execute(query)
            properties = result.scalars().all()

            items = []
            for property_obj in properties:
                response_data = await self._property_to_list_response(db, property_obj)
                items.append(response_data)

            return items

        except Exception as e:
            logger.error(
                "Failed to get featured properties", error=str(e), exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "FEATURED_PROPERTIES_FAILED",
                        "message": "Не удалось получить рекомендуемые объекты",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def upload_property_images(
        self,
        db: AsyncSession,
        property_id: str,
        files: List[UploadFile],
        developer_id: str,
        titles: Optional[List[str]] = None,
    ) -> List[dict]:
        """Upload property images."""
        try:
            # Verify property ownership
            db_property = await self._get_property_by_developer(
                db, property_id, developer_id
            )

            uploaded_images = []

            for i, file in enumerate(files):
                # Upload image
                file_url, thumbnail_url = await self.file_service.upload_property_image(
                    file=file,
                    property_id=property_id,
                    is_main=len(db_property.images) == 0,  # First image is main
                )

                # Create database record
                image_data = {
                    "property_id": property_id,
                    "url": file_url,
                    "title": titles[i] if titles and i < len(titles) else None,
                    "is_main": len(db_property.images) == 0,
                    "order": len(db_property.images),
                }

                db_image = PropertyImage(**image_data)
                db.add(db_image)
                await db.commit()
                await db.refresh(db_image)

                uploaded_images.append(
                    {
                        "id": str(db_image.id),
                        "url": file_url,
                        "thumbnail_url": thumbnail_url,
                        "title": db_image.title,
                        "is_main": db_image.is_main,
                        "order": db_image.order,
                    }
                )

            logger.info(
                "Property images uploaded successfully",
                property_id=property_id,
                images_count=len(uploaded_images),
            )

            return uploaded_images

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to upload property images",
                property_id=property_id,
                developer_id=developer_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "IMAGE_UPLOAD_FAILED",
                        "message": "Не удалось загрузить изображения",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def upload_property_documents(
        self,
        db: AsyncSession,
        property_id: str,
        files: List[UploadFile],
        developer_id: str,
        titles: List[str],
        document_types: List[str],
    ) -> List[dict]:
        """Upload property documents."""
        try:
            # Verify property ownership
            await self._get_property_by_developer(db, property_id, developer_id)

            uploaded_docs = []

            for i, file in enumerate(files):
                # Upload document
                file_url = await self.file_service.upload_property_document(
                    file=file, property_id=property_id
                )

                # Create database record
                doc_data = {
                    "property_id": property_id,
                    "title": titles[i] if i < len(titles) else file.filename,
                    "document_type": document_types[i]
                    if i < len(document_types)
                    else "OTHER",
                    "file_url": file_url,
                    "file_size": file.size or 0,
                    "mime_type": file.content_type or "application/octet-stream",
                }

                db_document = PropertyDocument(**doc_data)
                db.add(db_document)
                await db.commit()
                await db.refresh(db_document)

                uploaded_docs.append(
                    {
                        "id": str(db_document.id),
                        "title": db_document.title,
                        "document_type": db_document.document_type,
                        "file_url": file_url,
                        "file_size": db_document.file_size,
                        "mime_type": db_document.mime_type,
                    }
                )

            logger.info(
                "Property documents uploaded successfully",
                property_id=property_id,
                documents_count=len(uploaded_docs),
            )

            return uploaded_docs

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to upload property documents",
                property_id=property_id,
                developer_id=developer_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "DOCUMENT_UPLOAD_FAILED",
                        "message": "Не удалось загрузить документы",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def update_property_status(
        self,
        db: AsyncSession,
        property_id: str,
        status: PropertyStatus,
        developer_id: str,
    ) -> PropertyResponse:
        """Update property status."""
        try:
            # Get property and verify ownership
            db_property = await self._get_property_by_developer(
                db, property_id, developer_id
            )

            db_property.status = status
            await db.commit()
            await db.refresh(db_property)

            logger.info(
                "Property status updated successfully",
                property_id=property_id,
                new_status=status.value,
            )

            return await self._property_to_response(db, db_property)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to update property status",
                property_id=property_id,
                status=status.value if status else None,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "STATUS_UPDATE_FAILED",
                        "message": "Не удалось обновить статус объекта",
                        "details": {"error": str(e)},
                    }
                },
            )

    # Helper methods
    async def _get_verified_developer(
        self, db: AsyncSession, developer_id: str
    ) -> Developer:
        """Get verified developer or raise exception."""
        query = select(Developer).where(Developer.id == developer_id)
        result = await db.execute(query)
        developer = result.scalar_one_or_none()

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
                        "message": "Застройщик не прошел верификацию",
                        "details": {},
                    }
                },
            )

        return developer

    async def _get_property_by_developer(
        self, db: AsyncSession, property_id: str, developer_id: str
    ) -> Property:
        """Get property by developer or raise exception."""
        query = (
            select(Property)
            .options(selectinload(Property.images), selectinload(Property.documents))
            .where(
                and_(Property.id == property_id, Property.developer_id == developer_id)
            )
        )

        result = await db.execute(query)
        db_property = result.scalar_one_or_none()

        if not db_property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "PROPERTY_NOT_FOUND",
                        "message": "Объект недвижимости не найден или не принадлежит застройщику",
                        "details": {},
                    }
                },
            )

        return db_property

    def _apply_search_filters(
        self, query, search_params: PropertySearchParams, filters_applied: dict
    ):
        """Apply search filters to query."""
        if search_params.property_type:
            query = query.where(Property.property_type == search_params.property_type)
            filters_applied["property_type"] = search_params.property_type.value

        if search_params.deal_type:
            query = query.where(Property.deal_type == search_params.deal_type)
            filters_applied["deal_type"] = search_params.deal_type.value
        
        # Handle numeric type filter (0=дом, 1=квартира, 2=коммерческая)
        if search_params.type:
            type_mapping = {
                "0": PropertyType.HOUSE,
                "1": PropertyType.APARTMENT, 
                "2": PropertyType.COMMERCIAL
            }
            if search_params.type in type_mapping:
                query = query.where(Property.property_type == type_mapping[search_params.type])
                filters_applied["type"] = search_params.type

        if search_params.region:
            query = query.where(Property.region.ilike(f"%{search_params.region}%"))
            filters_applied["region"] = search_params.region

        if search_params.city:
            query = query.where(Property.city.ilike(f"%{search_params.city}%"))
            filters_applied["city"] = search_params.city

        if search_params.district:
            query = query.where(Property.district.ilike(f"%{search_params.district}%"))
            filters_applied["district"] = search_params.district

        if search_params.price_min:
            query = query.where(Property.price >= search_params.price_min)
            filters_applied["price_min"] = str(search_params.price_min)

        if search_params.price_max:
            query = query.where(Property.price <= search_params.price_max)
            filters_applied["price_max"] = str(search_params.price_max)

        if search_params.total_area_min:
            query = query.where(Property.total_area >= search_params.total_area_min)
            filters_applied["total_area_min"] = search_params.total_area_min

        if search_params.total_area_max:
            query = query.where(Property.total_area <= search_params.total_area_max)
            filters_applied["total_area_max"] = search_params.total_area_max

        if search_params.rooms_count:
            query = query.where(Property.rooms_count.in_(search_params.rooms_count))
            filters_applied["rooms_count"] = search_params.rooms_count

        if search_params.has_parking is not None:
            query = query.where(Property.has_parking == search_params.has_parking)
            filters_applied["has_parking"] = search_params.has_parking

        if search_params.has_balcony is not None:
            query = query.where(Property.has_balcony == search_params.has_balcony)
            filters_applied["has_balcony"] = search_params.has_balcony

        if search_params.has_elevator is not None:
            query = query.where(Property.has_elevator == search_params.has_elevator)
            filters_applied["has_elevator"] = search_params.has_elevator

        if search_params.renovation_type:
            query = query.where(
                Property.renovation_type == search_params.renovation_type
            )
            filters_applied["renovation_type"] = search_params.renovation_type.value

        if search_params.building_year_min:
            query = query.where(
                Property.building_year >= search_params.building_year_min
            )
            filters_applied["building_year_min"] = search_params.building_year_min

        if search_params.building_year_max:
            query = query.where(
                Property.building_year <= search_params.building_year_max
            )
            filters_applied["building_year_max"] = search_params.building_year_max

        if search_params.floor_min:
            query = query.where(Property.floor >= search_params.floor_min)
            filters_applied["floor_min"] = search_params.floor_min

        if search_params.floor_max:
            query = query.where(Property.floor <= search_params.floor_max)
            filters_applied["floor_max"] = search_params.floor_max

        if search_params.developer_id:
            query = query.where(Property.developer_id == search_params.developer_id)
            filters_applied["developer_id"] = search_params.developer_id

        if search_params.is_featured is not None:
            query = query.where(Property.is_featured == search_params.is_featured)
            filters_applied["is_featured"] = search_params.is_featured

        if search_params.search:
            search_term = f"%{search_params.search}%"
            query = query.where(
                or_(
                    Property.title.ilike(search_term),
                    Property.description.ilike(search_term),
                    Property.street.ilike(search_term),
                )
            )
            filters_applied["search"] = search_params.search

        # Enhanced rooms filter with 4+ logic
        if search_params.rooms:
            try:
                room_numbers = [int(x.strip()) for x in search_params.rooms.split(',') if x.strip().isdigit()]
                room_conditions = []
                for room_num in room_numbers:
                    if room_num >= 4:
                        # If 4 or more, include all rooms >= 4
                        room_conditions.append(Property.rooms_count >= 4)
                    else:
                        room_conditions.append(Property.rooms_count == room_num)
                
                if room_conditions:
                    query = query.where(or_(*room_conditions))
                    filters_applied["rooms"] = search_params.rooms
            except ValueError:
                pass  # Skip invalid room format
        
        # Peculiarity filter (feature-based filtering)
        if search_params.peculiarity:
            peculiarities = [p.strip().lower() for p in search_params.peculiarity.split(',')]
            peculiarity_conditions = []
            
            for peculiarity in peculiarities:
                if peculiarity == 'balcony':
                    peculiarity_conditions.append(or_(Property.has_balcony == True, Property.has_loggia == True))
                elif peculiarity == 'parking':
                    peculiarity_conditions.append(Property.has_parking == True)
                elif peculiarity == 'furniture':
                    peculiarity_conditions.append(Property.has_furniture == True)
                elif peculiarity == 'playground':
                    # For playground, we might need to add a field to Property model or join with Complex
                    # For now, we'll skip this or you can extend the Property model
                    pass
                elif peculiarity == 'gym':
                    # Similar to playground - might need complex-level features
                    pass
                elif peculiarity == 'ac':
                    # Might need additional field in Property model
                    pass
                elif peculiarity == 'appliances':
                    # Might need additional field in Property model  
                    pass
                elif peculiarity == 'concierge':
                    # Might need additional field in Property model
                    pass
            
            if peculiarity_conditions:
                query = query.where(and_(*peculiarity_conditions))
                filters_applied["peculiarity"] = search_params.peculiarity
        
        # Verify filter (developer verification and AI features)
        if search_params.verify:
            verify_options = [v.strip().lower() for v in search_params.verify.split(',')]
            verify_conditions = []
            
            for verify_option in verify_options:
                if verify_option == 'verified':
                    # Join with Developer table to check verification
                    from app.models import Developer
                    verify_conditions.append(Developer.is_verified == True)
                    # Note: This requires joining with Developer table in the main query
                elif verify_option == 'ai':
                    # For AI price evaluation, we might need additional fields
                    # This could be a flag in Property model or calculated field
                    pass
            
            if verify_conditions and 'verified' in [v.strip().lower() for v in search_params.verify.split(',')]:
                # We need to ensure Developer is joined in the main query for this filter
                filters_applied["verify"] = search_params.verify
        
        # Geographic search
        if search_params.lat and search_params.lng and search_params.radius:
            # Simple distance calculation (can be improved with PostGIS)
            lat_diff = 0.009 * search_params.radius  # Roughly 1km = 0.009 degrees
            lng_diff = 0.009 * search_params.radius

            query = query.where(
                and_(
                    Property.latitude.between(
                        search_params.lat - lat_diff, search_params.lat + lat_diff
                    ),
                    Property.longitude.between(
                        search_params.lng - lng_diff, search_params.lng + lng_diff
                    ),
                )
            )
            filters_applied["geographic"] = {
                "lat": search_params.lat,
                "lng": search_params.lng,
                "radius": search_params.radius,
            }

        return query

    def _apply_sorting(self, query, sort_option: str):
        """Apply sorting to query."""
        if sort_option == "price_asc":
            return query.order_by(Property.price.asc())
        elif sort_option == "price_desc":
            return query.order_by(Property.price.desc())
        elif sort_option == "date_asc" or sort_option == "data_asc":  # Support both spellings
            return query.order_by(Property.created_at.asc())
        elif sort_option == "date_desc" or sort_option == "data_desc":
            return query.order_by(Property.created_at.desc())
        elif sort_option == "area_asc":
            return query.order_by(Property.total_area.asc())
        elif sort_option == "area_desc":
            return query.order_by(Property.total_area.desc())
        elif sort_option == "popular":
            return query.order_by(
                Property.views_count.desc(), Property.favorites_count.desc()
            )
        else:  # date_desc (default)
            return query.order_by(Property.created_at.desc())

    async def _property_to_response(
        self, db: AsyncSession, property_obj: Property
    ) -> PropertyResponse:
        """Convert Property model to PropertyResponse."""
        try:
            # Ensure we have a fresh object with all data loaded
            await db.refresh(property_obj)
            
            # Get developer info
            if not property_obj.developer:
                developer_query = (
                    select(Developer)
                    .options(selectinload(Developer.user))
                    .where(Developer.id == property_obj.developer_id)
                )
                result = await db.execute(developer_query)
                developer = result.scalar_one()
            else:
                developer = property_obj.developer

            developer_info = {
                "id": str(developer.id),
                "company_name": developer.company_name,
                "is_verified": developer.is_verified,
                "rating": float(developer.rating) if developer.rating else 0.0,
                "logo_url": developer.logo_url,
            }

            # Convert images
            images = [
                {
                    "id": str(img.id),
                    "url": img.url,
                    "title": img.title,
                    "is_main": img.is_main,
                    "order": img.order,
                    "created_at": img.created_at,
                }
                for img in sorted(
                    property_obj.images, key=lambda x: (not x.is_main, x.order)
                )
            ]

            # Convert documents
            documents = [
                {
                    "id": str(doc.id),
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "file_url": doc.file_url,
                    "file_size": doc.file_size,
                    "mime_type": doc.mime_type,
                    "is_verified": doc.is_verified,
                    "created_at": doc.created_at,
                }
                for doc in property_obj.documents
            ]

            return PropertyResponse(
                id=str(property_obj.id),
                title=property_obj.title,
                description=property_obj.description,
                property_type=property_obj.property_type,
                deal_type=property_obj.deal_type,
                price=property_obj.price,
                price_per_sqm=property_obj.price_per_sqm,
                currency=property_obj.currency,
                region=property_obj.region,
                city=property_obj.city,
                district=property_obj.district,
                street=property_obj.street,
                house_number=property_obj.house_number,
                apartment_number=property_obj.apartment_number,
                postal_code=property_obj.postal_code,
                latitude=property_obj.latitude,
                longitude=property_obj.longitude,
                full_address=property_obj.full_address,
                total_area=property_obj.total_area,
                living_area=property_obj.living_area,
                kitchen_area=property_obj.kitchen_area,
                rooms_count=property_obj.rooms_count,
                bedrooms_count=property_obj.bedrooms_count,
                bathrooms_count=property_obj.bathrooms_count,
                floor=property_obj.floor,
                total_floors=property_obj.total_floors,
                building_year=property_obj.building_year,
                ceiling_height=property_obj.ceiling_height,
                has_balcony=property_obj.has_balcony,
                has_loggia=property_obj.has_loggia,
                has_elevator=property_obj.has_elevator,
                has_parking=property_obj.has_parking,
                has_furniture=property_obj.has_furniture,
                renovation_type=property_obj.renovation_type,
                status=property_obj.status,
                is_featured=property_obj.is_featured,
                views_count=property_obj.views_count,
                favorites_count=property_obj.favorites_count,
                available_from=property_obj.available_from,
                images=images,
                documents=documents,
                developer_id=str(property_obj.developer_id),
                developer=developer_info,
                created_at=property_obj.created_at,
                updated_at=property_obj.updated_at,
            )
        
        except Exception as e:
            logger.error(
                "Failed to convert property to response",
                property_id=str(property_obj.id),
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PROPERTY_CONVERSION_FAILED",
                        "message": "Не удалось подготовить данные объекта",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def delete_property_image(
        self, db: AsyncSession, property_id: str, image_id: str, developer_id: str
    ) -> bool:
        """Delete property image."""
        try:
            # Verify property ownership
            await self._get_property_by_developer(db, property_id, developer_id)
            
            # Get image
            query = (
                select(PropertyImage)
                .where(
                    and_(
                        PropertyImage.id == image_id,
                        PropertyImage.property_id == property_id
                    )
                )
            )
            result = await db.execute(query)
            db_image = result.scalar_one_or_none()
            
            if not db_image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "IMAGE_NOT_FOUND",
                            "message": "Изображение не найдено",
                            "details": {},
                        }
                    },
                )
            
            # Delete file from storage
            await self.file_service.delete_file(db_image.url)
            
            # Delete from database
            await db.delete(db_image)
            await db.commit()
            
            logger.info(
                "Property image deleted successfully",
                property_id=property_id,
                image_id=image_id,
                developer_id=developer_id,
            )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to delete property image",
                property_id=property_id,
                image_id=image_id,
                developer_id=developer_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "IMAGE_DELETION_FAILED",
                        "message": "Не удалось удалить изображение",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def delete_property_document(
        self, db: AsyncSession, property_id: str, document_id: str, developer_id: str
    ) -> bool:
        """Delete property document."""
        try:
            # Verify property ownership
            await self._get_property_by_developer(db, property_id, developer_id)
            
            # Get document
            query = (
                select(PropertyDocument)
                .where(
                    and_(
                        PropertyDocument.id == document_id,
                        PropertyDocument.property_id == property_id
                    )
                )
            )
            result = await db.execute(query)
            db_document = result.scalar_one_or_none()
            
            if not db_document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "DOCUMENT_NOT_FOUND",
                            "message": "Документ не найден",
                            "details": {},
                        }
                    },
                )
            
            # Delete file from storage
            await self.file_service.delete_file(db_document.file_url)
            
            # Delete from database
            await db.delete(db_document)
            await db.commit()
            
            logger.info(
                "Property document deleted successfully",
                property_id=property_id,
                document_id=document_id,
                developer_id=developer_id,
            )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to delete property document",
                property_id=property_id,
                document_id=document_id,
                developer_id=developer_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "DOCUMENT_DELETION_FAILED",
                        "message": "Не удалось удалить документ",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def _property_to_list_response(
        self, db: AsyncSession, property_obj: Property
    ) -> PropertyListResponse:
        """Convert Property model to PropertyListResponse."""
        # Get developer info
        if not property_obj.developer:
            developer_query = select(Developer).where(
                Developer.id == property_obj.developer_id
            )
            result = await db.execute(developer_query)
            developer = result.scalar_one()
        else:
            developer = property_obj.developer

        # Get main image
        main_image_url = None
        if property_obj.images:
            main_image = next(
                (img for img in property_obj.images if img.is_main),
                property_obj.images[0],
            )
            main_image_url = main_image.url

        return PropertyListResponse(
            id=str(property_obj.id),
            title=property_obj.title,
            property_type=property_obj.property_type,
            deal_type=property_obj.deal_type,
            price=property_obj.price,
            price_per_sqm=property_obj.price_per_sqm,
            currency=property_obj.currency,
            city=property_obj.city,
            district=property_obj.district,
            total_area=property_obj.total_area,
            rooms_count=property_obj.rooms_count,
            floor=property_obj.floor,
            total_floors=property_obj.total_floors,
            has_parking=property_obj.has_parking,
            renovation_type=property_obj.renovation_type,
            status=property_obj.status,
            is_featured=property_obj.is_featured,
            views_count=property_obj.views_count,
            favorites_count=property_obj.favorites_count,
            main_image_url=main_image_url,
            developer_id=str(property_obj.developer_id),
            developer_name=developer.company_name,
            developer_verified=developer.is_verified,
            created_at=property_obj.created_at,
            updated_at=property_obj.updated_at,
        )
