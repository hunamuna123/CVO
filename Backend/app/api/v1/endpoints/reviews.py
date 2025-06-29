"""
Reviews API endpoints for property and developer reviews.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.review import (
    ReviewCreateRequest,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdateRequest,
    ReviewSearchParams,
)
from app.services.review_service import ReviewService
from app.utils.security import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

# Initialize the review service
review_service = ReviewService()


@router.get(
    "",
    response_model=List[ReviewListResponse],
    summary="Get reviews with filtering",
    description="Get reviews with filtering and pagination",
)
async def get_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    developer_id: Optional[str] = Query(None, description="Filter by developer ID"),
    property_id: Optional[str] = Query(None, description="Filter by property ID"),
    rating_min: Optional[int] = Query(
        None, ge=1, le=5, description="Minimum rating filter"
    ),
    rating_max: Optional[int] = Query(
        None, ge=1, le=5, description="Maximum rating filter"
    ),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    sort: Optional[str] = Query(
        "created_desc",
        description="Sort by: created_desc, created_asc, rating_desc, rating_asc",
    ),
    db: AsyncSession = Depends(get_db),
) -> List[ReviewListResponse]:
    """
    Get reviews with filtering and pagination.

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **developer_id**: Filter reviews by specific developer
    - **property_id**: Filter reviews by specific property
    - **rating_min**: Minimum rating (1-5)
    - **rating_max**: Maximum rating (1-5)
    - **is_verified**: Filter by verification status
    - **sort**: Sorting option

    Returns paginated list of reviews with user and target information.
    """
    search_params = ReviewSearchParams(
        page=page,
        limit=limit,
        developer_id=developer_id,
        property_id=property_id,
        rating_min=rating_min,
        rating_max=rating_max,
        is_verified=is_verified,
        sort=sort,
    )

    return await review_service.search_reviews(db, search_params)


@router.get(
    "/stats",
    response_model=dict,
    summary="Get review statistics",
    description="Get review statistics for developer or property",
)
async def get_review_stats(
    developer_id: Optional[str] = Query(None, description="Developer ID for stats"),
    property_id: Optional[str] = Query(None, description="Property ID for stats"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get review statistics.

    **Query parameters:**
    - **developer_id**: Get stats for specific developer
    - **property_id**: Get stats for specific property

    **Note:** Exactly one of developer_id or property_id must be provided.

    Returns statistics including:
    - Average rating
    - Total review count
    - Rating distribution (1-5 stars)
    """
    if not developer_id and not property_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "MISSING_FILTER",
                    "message": "Необходимо указать developer_id или property_id",
                    "details": {},
                }
            },
        )

    if developer_id and property_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "MULTIPLE_FILTERS",
                    "message": "Нельзя указывать одновременно developer_id и property_id",
                    "details": {},
                }
            },
        )

    return await review_service.get_review_stats(db, developer_id, property_id)


@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Get review details",
    description="Get detailed information about a specific review",
)
async def get_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """
    Get detailed review information by ID.

    **Path parameters:**
    - **review_id**: Review UUID

    Returns complete review information including user and target details.
    """
    return await review_service.get_review_by_id(db, review_id)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create review",
    description="Create a new review for developer or property",
)
async def create_review(
    review_data: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """
    Create a new review.

    **Requirements:**
    - Valid access token in Authorization header

    **Request body:**
    - **developer_id**: UUID of the developer (required)
    - **property_id**: UUID of the property (optional)
    - **rating**: Rating from 1 to 5 (required)
    - **title**: Review title (required)
    - **content**: Review content (required)

    **Business rules:**
    - User can only review each developer/property combination once
    - Property reviews must include developer_id
    - Rating must be between 1 and 5
    - Content must be at least 10 characters
    """
    return await review_service.create_review(db, review_data, str(current_user.id))


@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
    summary="Update review",
    description="Update an existing review (author only)",
)
async def update_review(
    review_id: str,
    review_data: ReviewUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReviewResponse:
    """
    Update an existing review.

    **Requirements:**
    - Valid access token in Authorization header
    - Must be the review author

    **Updatable fields:**
    - **rating**: New rating (1-5)
    - **title**: New title
    - **content**: New content

    **Business rules:**
    - Only the review author can update their review
    - Updated reviews may require re-verification
    - Rating changes affect overall statistics
    """
    return await review_service.update_review(
        db, review_id, review_data, str(current_user.id)
    )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete review",
    description="Delete a review (author only)",
)
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a review.

    **Requirements:**
    - Valid access token in Authorization header
    - Must be the review author

    **Warning:** This action cannot be undone.
    Deleting a review affects overall rating statistics.
    """
    await review_service.delete_review(db, review_id, str(current_user.id))
    return {"message": "Review deleted successfully"}


@router.get(
    "/my/reviews",
    response_model=List[ReviewListResponse],
    summary="Get user's reviews",
    description="Get all reviews created by the current user",
)
async def get_my_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ReviewListResponse]:
    """
    Get all reviews created by the current user.

    **Requirements:**
    - Valid access token in Authorization header

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)

    Returns paginated list of user's reviews.
    """
    return await review_service.get_user_reviews(
        db, str(current_user.id), page, limit
    )
