"""
Review service for managing property and developer reviews.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.review import Review
from app.models.property import Property
from app.models.developer import Developer
from app.models.user import User
from app.schemas.review import (
    ReviewCreateRequest,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdateRequest,
    ReviewSearchParams,
    UserInfo,
    DeveloperInfo,
    PropertyInfo,
)
import structlog

logger = structlog.get_logger(__name__)


class ReviewService:
    """Service for managing reviews."""

    async def search_reviews(
        self,
        db: AsyncSession,
        search_params: ReviewSearchParams,
    ) -> List[ReviewListResponse]:
        """
        Search reviews with filtering and pagination.
        
        Args:
            db: Database session
            search_params: Search parameters
            
        Returns:
            List of reviews matching criteria
        """
        offset = (search_params.page - 1) * search_params.limit

        # Build query
        query = (
            select(Review)
            .options(
                selectinload(Review.user),
                selectinload(Review.developer),
                selectinload(Review.property),
            )
        )

        # Apply filters
        if search_params.developer_id:
            query = query.where(Review.developer_id == UUID(search_params.developer_id))
        
        if search_params.property_id:
            query = query.where(Review.property_id == UUID(search_params.property_id))
        
        if search_params.rating_min:
            query = query.where(Review.rating >= search_params.rating_min)
        
        if search_params.rating_max:
            query = query.where(Review.rating <= search_params.rating_max)
        
        if search_params.is_verified is not None:
            query = query.where(Review.is_verified == search_params.is_verified)

        # Apply sorting
        if search_params.sort == "created_desc":
            query = query.order_by(Review.created_at.desc())
        elif search_params.sort == "created_asc":
            query = query.order_by(Review.created_at.asc())
        elif search_params.sort == "rating_desc":
            query = query.order_by(Review.rating.desc())
        elif search_params.sort == "rating_asc":
            query = query.order_by(Review.rating.asc())
        else:
            query = query.order_by(Review.created_at.desc())

        # Apply pagination
        query = query.offset(offset).limit(search_params.limit)

        result = await db.execute(query)
        reviews = result.scalars().all()

        # Convert to response format
        review_responses = []
        for review in reviews:
            user_info = UserInfo(
                id=str(review.user.id),
                first_name=review.user.first_name,
                last_name=review.user.last_name,
                avatar_url=review.user.avatar_url,
            )

            developer_info = DeveloperInfo(
                id=str(review.developer.id),
                company_name=review.developer.company_name,
                logo_url=review.developer.logo_url,
            )

            property_info = None
            if review.property:
                property_info = PropertyInfo(
                    id=str(review.property.id),
                    title=review.property.title,
                    property_type=review.property.property_type,
                )

            review_responses.append(
                ReviewListResponse(
                    id=str(review.id),
                    rating=review.rating,
                    title=review.title,
                    content=review.content,
                    is_verified=review.is_verified,
                    created_at=review.created_at,
                    user=user_info,
                    developer=developer_info,
                    property=property_info,
                )
            )

        logger.info(
            "Searched reviews",
            filters=search_params.dict(),
            results_count=len(review_responses),
        )

        return review_responses

    async def get_review_stats(
        self,
        db: AsyncSession,
        developer_id: Optional[str] = None,
        property_id: Optional[str] = None,
    ) -> dict:
        """
        Get review statistics for developer or property.
        
        Args:
            db: Database session
            developer_id: Developer UUID (optional)
            property_id: Property UUID (optional)
            
        Returns:
            Statistics dictionary
        """
        # Build base query
        base_query = select(Review).where(Review.is_verified == True)

        if developer_id:
            base_query = base_query.where(Review.developer_id == UUID(developer_id))
        
        if property_id:
            base_query = base_query.where(Review.property_id == UUID(property_id))

        # Get total count
        count_query = select(func.count(Review.id)).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        if total_count == 0:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0,
                }
            }

        # Get average rating
        avg_query = select(func.avg(Review.rating)).select_from(base_query.subquery())
        avg_result = await db.execute(avg_query)
        average_rating = float(avg_result.scalar() or 0.0)

        # Get rating distribution
        distribution_query = (
            select(Review.rating, func.count(Review.id))
            .select_from(base_query.subquery())
            .group_by(Review.rating)
        )
        distribution_result = await db.execute(distribution_query)
        distribution_data = distribution_result.all()

        rating_distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for rating, count in distribution_data:
            rating_distribution[str(rating)] = count

        stats = {
            "total_reviews": total_count,
            "average_rating": round(average_rating, 2),
            "rating_distribution": rating_distribution,
        }

        logger.info(
            "Generated review statistics",
            developer_id=developer_id,
            property_id=property_id,
            stats=stats,
        )

        return stats

    async def get_review_by_id(
        self,
        db: AsyncSession,
        review_id: str,
    ) -> ReviewResponse:
        """
        Get review by ID.
        
        Args:
            db: Database session
            review_id: Review UUID
            
        Returns:
            Review details
            
        Raises:
            NotFoundException: If review doesn't exist
        """
        query = (
            select(Review)
            .options(
                selectinload(Review.user),
                selectinload(Review.developer),
                selectinload(Review.property),
            )
            .where(Review.id == UUID(review_id))
        )

        result = await db.execute(query)
        review = result.scalar_one_or_none()

        if not review:
            raise NotFoundException(
                message="Отзыв не найден",
                details={"review_id": review_id}
            )

        # Build response
        user_info = UserInfo(
            id=str(review.user.id),
            first_name=review.user.first_name,
            last_name=review.user.last_name,
            avatar_url=review.user.avatar_url,
        )

        developer_info = DeveloperInfo(
            id=str(review.developer.id),
            company_name=review.developer.company_name,
            logo_url=review.developer.logo_url,
        )

        property_info = None
        if review.property:
            property_info = PropertyInfo(
                id=str(review.property.id),
                title=review.property.title,
                property_type=review.property.property_type,
            )

        return ReviewResponse(
            id=str(review.id),
            user_id=str(review.user_id),
            developer_id=str(review.developer_id),
            property_id=str(review.property_id) if review.property_id else None,
            rating=review.rating,
            title=review.title,
            content=review.content,
            is_verified=review.is_verified,
            created_at=review.created_at,
            updated_at=review.updated_at,
            user=user_info,
            developer=developer_info,
            property=property_info,
        )

    async def create_review(
        self,
        db: AsyncSession,
        review_data: ReviewCreateRequest,
        user_id: str,
    ) -> ReviewResponse:
        """
        Create a new review.
        
        Args:
            db: Database session
            review_data: Review data
            user_id: User UUID
            
        Returns:
            Created review
            
        Raises:
            NotFoundException: If developer/property doesn't exist
            ConflictException: If user already reviewed this developer/property
        """
        # Verify developer exists
        developer_query = select(Developer).where(Developer.id == UUID(review_data.developer_id))
        developer_result = await db.execute(developer_query)
        developer = developer_result.scalar_one_or_none()

        if not developer:
            raise NotFoundException(
                message="Застройщик не найден",
                details={"developer_id": review_data.developer_id}
            )

        # Verify property exists (if provided)
        property_obj = None
        if review_data.property_id:
            property_query = select(Property).where(
                and_(
                    Property.id == UUID(review_data.property_id),
                    Property.developer_id == UUID(review_data.developer_id)
                )
            )
            property_result = await db.execute(property_query)
            property_obj = property_result.scalar_one_or_none()

            if not property_obj:
                raise NotFoundException(
                    message="Объект недвижимости не найден или не принадлежит указанному застройщику",
                    details={
                        "property_id": review_data.property_id,
                        "developer_id": review_data.developer_id
                    }
                )

        # Check if user already reviewed this developer/property combination
        existing_query = select(Review).where(
            and_(
                Review.user_id == UUID(user_id),
                Review.developer_id == UUID(review_data.developer_id),
                Review.property_id == UUID(review_data.property_id) if review_data.property_id else Review.property_id.is_(None)
            )
        )
        existing_result = await db.execute(existing_query)
        existing_review = existing_result.scalar_one_or_none()

        if existing_review:
            raise ConflictException(
                message="Вы уже оставили отзыв для этого застройщика/объекта",
                details={
                    "existing_review_id": str(existing_review.id),
                    "developer_id": review_data.developer_id,
                    "property_id": review_data.property_id,
                }
            )

        # Create review
        review = Review(
            user_id=UUID(user_id),
            developer_id=UUID(review_data.developer_id),
            property_id=UUID(review_data.property_id) if review_data.property_id else None,
            rating=review_data.rating,
            title=review_data.title,
            content=review_data.content,
            is_verified=False,  # Reviews require moderation
        )

        db.add(review)
        await db.commit()
        await db.refresh(review)

        # Update developer rating
        await self._update_developer_rating(db, review_data.developer_id)

        logger.info(
            "Created review",
            review_id=str(review.id),
            user_id=user_id,
            developer_id=review_data.developer_id,
            property_id=review_data.property_id,
        )

        # Return created review
        return await self.get_review_by_id(db, str(review.id))

    async def update_review(
        self,
        db: AsyncSession,
        review_id: str,
        review_data: ReviewUpdateRequest,
        user_id: str,
    ) -> ReviewResponse:
        """
        Update an existing review.
        
        Args:
            db: Database session
            review_id: Review UUID
            review_data: Updated review data
            user_id: User UUID (must be review author)
            
        Returns:
            Updated review
            
        Raises:
            NotFoundException: If review doesn't exist
            BadRequestException: If user is not the author
        """
        # Get existing review
        query = select(Review).where(Review.id == UUID(review_id))
        result = await db.execute(query)
        review = result.scalar_one_or_none()

        if not review:
            raise NotFoundException(
                message="Отзыв не найден",
                details={"review_id": review_id}
            )

        # Check ownership
        if str(review.user_id) != user_id:
            raise BadRequestException(
                message="Вы можете редактировать только свои отзывы",
                details={"review_id": review_id, "user_id": user_id}
            )

        # Update fields
        if review_data.rating is not None:
            review.rating = review_data.rating
        
        if review_data.title is not None:
            review.title = review_data.title
        
        if review_data.content is not None:
            review.content = review_data.content

        # Mark as unverified if content changed
        if review_data.title or review_data.content:
            review.is_verified = False

        await db.commit()
        await db.refresh(review)

        # Update developer rating if rating changed
        if review_data.rating is not None:
            await self._update_developer_rating(db, str(review.developer_id))

        logger.info(
            "Updated review",
            review_id=review_id,
            user_id=user_id,
            updated_fields=review_data.dict(exclude_unset=True),
        )

        return await self.get_review_by_id(db, review_id)

    async def delete_review(
        self,
        db: AsyncSession,
        review_id: str,
        user_id: str,
    ) -> None:
        """
        Delete a review.
        
        Args:
            db: Database session
            review_id: Review UUID
            user_id: User UUID (must be review author)
            
        Raises:
            NotFoundException: If review doesn't exist
            BadRequestException: If user is not the author
        """
        # Get existing review
        query = select(Review).where(Review.id == UUID(review_id))
        result = await db.execute(query)
        review = result.scalar_one_or_none()

        if not review:
            raise NotFoundException(
                message="Отзыв не найден",
                details={"review_id": review_id}
            )

        # Check ownership
        if str(review.user_id) != user_id:
            raise BadRequestException(
                message="Вы можете удалять только свои отзывы",
                details={"review_id": review_id, "user_id": user_id}
            )

        developer_id = str(review.developer_id)

        # Delete review
        await db.delete(review)
        await db.commit()

        # Update developer rating
        await self._update_developer_rating(db, developer_id)

        logger.info(
            "Deleted review",
            review_id=review_id,
            user_id=user_id,
            developer_id=developer_id,
        )

    async def get_user_reviews(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        limit: int = 20,
    ) -> List[ReviewListResponse]:
        """
        Get all reviews created by a user.
        
        Args:
            db: Database session
            user_id: User UUID
            page: Page number
            limit: Items per page
            
        Returns:
            List of user's reviews
        """
        offset = (page - 1) * limit

        query = (
            select(Review)
            .options(
                selectinload(Review.user),
                selectinload(Review.developer),
                selectinload(Review.property),
            )
            .where(Review.user_id == UUID(user_id))
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await db.execute(query)
        reviews = result.scalars().all()

        # Convert to response format
        review_responses = []
        for review in reviews:
            user_info = UserInfo(
                id=str(review.user.id),
                first_name=review.user.first_name,
                last_name=review.user.last_name,
                avatar_url=review.user.avatar_url,
            )

            developer_info = DeveloperInfo(
                id=str(review.developer.id),
                company_name=review.developer.company_name,
                logo_url=review.developer.logo_url,
            )

            property_info = None
            if review.property:
                property_info = PropertyInfo(
                    id=str(review.property.id),
                    title=review.property.title,
                    property_type=review.property.property_type,
                )

            review_responses.append(
                ReviewListResponse(
                    id=str(review.id),
                    rating=review.rating,
                    title=review.title,
                    content=review.content,
                    is_verified=review.is_verified,
                    created_at=review.created_at,
                    user=user_info,
                    developer=developer_info,
                    property=property_info,
                )
            )

        logger.info(
            "Retrieved user reviews",
            user_id=user_id,
            page=page,
            limit=limit,
            count=len(review_responses),
        )

        return review_responses

    async def _update_developer_rating(
        self,
        db: AsyncSession,
        developer_id: str,
    ) -> None:
        """
        Update developer's average rating and review count.
        
        Args:
            db: Database session
            developer_id: Developer UUID
        """
        # Calculate new rating and count
        stats_query = (
            select(
                func.avg(Review.rating).label('avg_rating'),
                func.count(Review.id).label('review_count')
            )
            .where(
                and_(
                    Review.developer_id == UUID(developer_id),
                    Review.is_verified == True
                )
            )
        )

        stats_result = await db.execute(stats_query)
        stats = stats_result.first()

        avg_rating = float(stats.avg_rating) if stats.avg_rating else 0.0
        review_count = stats.review_count or 0

        # Update developer
        developer_query = select(Developer).where(Developer.id == UUID(developer_id))
        developer_result = await db.execute(developer_query)
        developer = developer_result.scalar_one_or_none()

        if developer:
            developer.rating = avg_rating
            developer.reviews_count = review_count
            await db.commit()

            logger.debug(
                "Updated developer rating",
                developer_id=developer_id,
                avg_rating=avg_rating,
                reviews_count=review_count,
            )
