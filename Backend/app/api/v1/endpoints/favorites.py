"""
Favorites API endpoints for managing user favorite properties.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.favorite import (
    FavoriteCreateRequest,
    FavoriteListResponse,
    FavoriteResponse,
)
from app.services.favorite_service import FavoriteService
from app.utils.security import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])

# Initialize the favorite service
favorite_service = FavoriteService()


@router.get(
    "",
    response_model=List[FavoriteListResponse],
    summary="Get user favorites",
    description="Get list of user's favorite properties with pagination",
)
async def get_user_favorites(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[FavoriteListResponse]:
    """
    Get user's favorite properties.

    **Requirements:**
    - Valid access token in Authorization header

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)

    Returns paginated list of favorite properties with basic information.
    """
    return await favorite_service.get_user_favorites(
        db, str(current_user.id), page, limit
    )


@router.post(
    "",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add to favorites",
    description="Add a property to user's favorites",
)
async def add_to_favorites(
    request: FavoriteCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FavoriteResponse:
    """
    Add property to favorites.

    **Requirements:**
    - Valid access token in Authorization header

    **Request body:**
    - **property_id**: UUID of the property to add to favorites

    **Notes:**
    - If property is already in favorites, returns existing favorite
    - Property must exist and be active
    """
    return await favorite_service.add_to_favorites(
        db, str(current_user.id), request.property_id
    )


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove from favorites",
    description="Remove a property from user's favorites",
)
async def remove_from_favorites(
    property_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Remove property from favorites.

    **Requirements:**
    - Valid access token in Authorization header

    **Path parameters:**
    - **property_id**: UUID of the property to remove from favorites

    **Notes:**
    - If property is not in favorites, returns success anyway
    - This is an idempotent operation
    """
    await favorite_service.remove_from_favorites(
        db, str(current_user.id), property_id
    )
    return {"message": "Property removed from favorites"}


@router.get(
    "/check/{property_id}",
    response_model=dict,
    summary="Check if property is favorited",
    description="Check if a specific property is in user's favorites",
)
async def check_favorite_status(
    property_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Check if property is in user's favorites.

    **Requirements:**
    - Valid access token in Authorization header

    **Path parameters:**
    - **property_id**: UUID of the property to check

    Returns boolean indicating if property is favorited.
    """
    is_favorited = await favorite_service.check_favorite_status(
        db, str(current_user.id), property_id
    )
    return {
        "property_id": property_id,
        "is_favorited": is_favorited,
    }


@router.get(
    "/count",
    response_model=dict,
    summary="Get favorites count",
    description="Get total count of user's favorite properties",
)
async def get_favorites_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get total count of user's favorites.

    **Requirements:**
    - Valid access token in Authorization header

    Returns total number of properties in user's favorites.
    """
    count = await favorite_service.get_favorites_count(db, str(current_user.id))
    return {"count": count}
