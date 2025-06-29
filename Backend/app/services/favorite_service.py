"""
Favorite service for managing user favorite properties.
"""

from typing import List
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ConflictException
from app.models.favorite import Favorite
from app.models.property import Property
from app.models.user import User
from app.schemas.favorite import (
    FavoriteListResponse,
    FavoriteResponse,
)
import structlog

logger = structlog.get_logger(__name__)


class FavoriteService:
    """Service for managing favorite properties."""

    async def get_user_favorites(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> List[FavoriteListResponse]:
        """
        Get user's favorite properties with pagination.
        
        Args:
            db: Database session
            user_id: User UUID
            page: Page number
            limit: Items per page
            
        Returns:
            List of favorite properties
        """
        offset = (page - 1) * limit

        # Query favorites with property details
        query = (
            select(Favorite)
            .options(
                selectinload(Favorite.property_obj).selectinload(Property.developer),
                selectinload(Favorite.property_obj).selectinload(Property.images),
            )
            .where(Favorite.user_id == UUID(user_id))
            .order_by(Favorite.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(query)
        favorites = result.scalars().all()

        # Convert to response format
        favorite_responses = []
        for favorite in favorites:
            if favorite.property_obj:  # Ensure property still exists
                property_data = {
                    "id": str(favorite.property_obj.id),
                    "title": favorite.property_obj.title,
                    "price": float(favorite.property_obj.price) if favorite.property_obj.price else None,
                    "city": favorite.property_obj.city,
                    "property_type": favorite.property_obj.property_type,
                    "total_area": float(favorite.property_obj.total_area) if favorite.property_obj.total_area else None,
                    "rooms_count": favorite.property_obj.rooms_count,
                    "main_image_url": None,
                    "developer": {
                        "id": str(favorite.property_obj.developer.id),
                        "company_name": favorite.property_obj.developer.company_name,
                    } if favorite.property_obj.developer else None,
                }

                # Get main image
                if favorite.property_obj.images:
                    main_image = next(
                        (img for img in favorite.property_obj.images if img.is_main),
                        favorite.property_obj.images[0] if favorite.property_obj.images else None
                    )
                    if main_image:
                        property_data["main_image_url"] = main_image.url

                favorite_responses.append(
                    FavoriteListResponse(
                        id=str(favorite.id),
                        property_id=str(favorite.property_id),
                        created_at=favorite.created_at,
                        property=property_data,
                    )
                )

        logger.info(
            "Retrieved user favorites",
            user_id=user_id,
            page=page,
            limit=limit,
            count=len(favorite_responses),
        )

        return favorite_responses

    async def add_to_favorites(
        self,
        db: AsyncSession,
        user_id: str,
        property_id: str,
    ) -> FavoriteResponse:
        """
        Add property to user's favorites.
        
        Args:
            db: Database session
            user_id: User UUID
            property_id: Property UUID
            
        Returns:
            Created favorite
            
        Raises:
            NotFoundException: If property doesn't exist
            ConflictException: If already in favorites
        """
        # Check if property exists and is active
        property_query = select(Property).where(
            and_(
                Property.id == UUID(property_id),
                Property.status == "ACTIVE"
            )
        )
        property_result = await db.execute(property_query)
        property_obj = property_result.scalar_one_or_none()

        if not property_obj:
            raise NotFoundException(
                message="Объект недвижимости не найден или неактивен",
                details={"property_id": property_id}
            )

        # Check if already in favorites
        existing_query = select(Favorite).where(
            and_(
                Favorite.user_id == UUID(user_id),
                Favorite.property_id == UUID(property_id)
            )
        )
        existing_result = await db.execute(existing_query)
        existing_favorite = existing_result.scalar_one_or_none()

        if existing_favorite:
            # Return existing favorite
            logger.info(
                "Property already in favorites",
                user_id=user_id,
                property_id=property_id,
            )
            return FavoriteResponse(
                id=str(existing_favorite.id),
                user_id=str(existing_favorite.user_id),
                property_id=str(existing_favorite.property_id),
                created_at=existing_favorite.created_at,
            )

        # Create new favorite
        favorite = Favorite(
            user_id=UUID(user_id),
            property_id=UUID(property_id),
        )

        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)

        # Update property favorites count
        await self._update_property_favorites_count(db, property_id)

        logger.info(
            "Added property to favorites",
            user_id=user_id,
            property_id=property_id,
            favorite_id=str(favorite.id),
        )

        return FavoriteResponse(
            id=str(favorite.id),
            user_id=str(favorite.user_id),
            property_id=str(favorite.property_id),
            created_at=favorite.created_at,
        )

    async def remove_from_favorites(
        self,
        db: AsyncSession,
        user_id: str,
        property_id: str,
    ) -> None:
        """
        Remove property from user's favorites.
        
        Args:
            db: Database session
            user_id: User UUID
            property_id: Property UUID
        """
        # Find and delete favorite
        query = select(Favorite).where(
            and_(
                Favorite.user_id == UUID(user_id),
                Favorite.property_id == UUID(property_id)
            )
        )
        result = await db.execute(query)
        favorite = result.scalar_one_or_none()

        if favorite:
            await db.delete(favorite)
            await db.commit()

            # Update property favorites count
            await self._update_property_favorites_count(db, property_id)

            logger.info(
                "Removed property from favorites",
                user_id=user_id,
                property_id=property_id,
                favorite_id=str(favorite.id),
            )
        else:
            logger.info(
                "Property was not in favorites",
                user_id=user_id,
                property_id=property_id,
            )

    async def check_favorite_status(
        self,
        db: AsyncSession,
        user_id: str,
        property_id: str,
    ) -> bool:
        """
        Check if property is in user's favorites.
        
        Args:
            db: Database session
            user_id: User UUID
            property_id: Property UUID
            
        Returns:
            True if property is favorited, False otherwise
        """
        query = select(Favorite).where(
            and_(
                Favorite.user_id == UUID(user_id),
                Favorite.property_id == UUID(property_id)
            )
        )
        result = await db.execute(query)
        favorite = result.scalar_one_or_none()

        return favorite is not None

    async def get_favorites_count(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> int:
        """
        Get total count of user's favorites.
        
        Args:
            db: Database session
            user_id: User UUID
            
        Returns:
            Total count of favorites
        """
        query = (
            select(func.count(Favorite.id))
            .where(Favorite.user_id == UUID(user_id))
        )
        result = await db.execute(query)
        count = result.scalar() or 0

        return count

    async def _update_property_favorites_count(
        self,
        db: AsyncSession,
        property_id: str,
    ) -> None:
        """
        Update the favorites count for a property.
        
        Args:
            db: Database session
            property_id: Property UUID
        """
        # Count current favorites
        count_query = (
            select(func.count(Favorite.id))
            .where(Favorite.property_id == UUID(property_id))
        )
        count_result = await db.execute(count_query)
        count = count_result.scalar() or 0

        # Update property
        property_query = select(Property).where(Property.id == UUID(property_id))
        property_result = await db.execute(property_query)
        property_obj = property_result.scalar_one_or_none()

        if property_obj:
            property_obj.favorites_count = count
            await db.commit()

            logger.debug(
                "Updated property favorites count",
                property_id=property_id,
                favorites_count=count,
            )
