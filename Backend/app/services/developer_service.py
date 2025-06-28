"""
Developer services for handling developer registration, management, and verification.
"""

import logging
from typing import List, Optional, Tuple
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Developer, Property, PropertyStatus, User, UserRole
from app.models.developer import VerificationStatus
from app.schemas.auth import AuthResponse
from app.schemas.developer import (
    DeveloperListResponse,
    DeveloperRegisterRequest,
    DeveloperResponse,
    DeveloperSearchParams,
    DeveloperUpdateRequest,
    DeveloperVerificationRequest,
)

logger = logging.getLogger(__name__)


class DeveloperService:
    """
    Service class for developer-related operations.
    """

    async def register_developer(
        self, db: AsyncSession, request: DeveloperRegisterRequest
    ) -> AuthResponse:
        """
        Register a new developer company.

        This creates both a User account (with DEVELOPER role) and a Developer profile.
        """
        # Check if phone already exists
        existing_user = await db.execute(
            select(User).where(User.phone == request.phone)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered",
            )

        # Check if email already exists
        existing_email = await db.execute(
            select(User).where(User.email == request.email)
        )
        if existing_email.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if INN already exists
        existing_inn = await db.execute(
            select(Developer).where(Developer.inn == request.inn)
        )
        if existing_inn.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this INN already registered",
            )

        # Create User account with DEVELOPER role
        user = User(
            phone=request.phone,
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            middle_name=request.middle_name,
            role=UserRole.DEVELOPER,
            is_verified=False,  # Will be verified via SMS
        )
        db.add(user)
        await db.flush()  # Get user.id

        # Create Developer profile
        developer = Developer(
            user_id=user.id,
            company_name=request.company_name,
            legal_name=request.legal_name,
            inn=request.inn,
            ogrn=request.ogrn,
            legal_address=request.legal_address,
            contact_phone=request.contact_phone,
            contact_email=request.contact_email,
            website=request.website,
            description=request.description,
            verification_status=VerificationStatus.PENDING,
        )
        db.add(developer)
        await db.commit()

        session_id = str(uuid4())
        logger.info(
            "Developer registration initiated for company %s (INN: %s) with session ID %s",
            request.company_name,
            request.inn,
            session_id,
        )

        return AuthResponse(
            message="Заявка на регистрацию застройщика отправлена. SMS с кодом отправлен.",
            session_id=session_id,
        )

    async def get_developer_by_id(
        self, db: AsyncSession, developer_id: str
    ) -> DeveloperResponse:
        """
        Get developer by ID with statistics.
        """
        # Get developer with user info
        result = await db.execute(
            select(Developer)
            .options(selectinload(Developer.user))
            .where(Developer.id == developer_id)
        )
        developer = result.scalar_one_or_none()

        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
            )

        # Get properties count
        properties_count_result = await db.execute(
            select(func.count(Property.id)).where(Property.developer_id == developer_id)
        )
        properties_count = properties_count_result.scalar() or 0

        # Get active properties count
        active_properties_count_result = await db.execute(
            select(func.count(Property.id)).where(
                and_(
                    Property.developer_id == developer_id,
                    Property.status == PropertyStatus.ACTIVE,
                )
            )
        )
        active_properties_count = active_properties_count_result.scalar() or 0

        # Create response with additional statistics
        response_data = {
            "id": str(developer.id),
            "user_id": str(developer.user_id),
            "company_name": developer.company_name,
            "legal_name": developer.legal_name,
            "inn": developer.inn,
            "ogrn": developer.ogrn,
            "legal_address": developer.legal_address,
            "contact_phone": developer.contact_phone,
            "contact_email": developer.contact_email,
            "website": developer.website,
            "description": developer.description,
            "logo_url": developer.logo_url,
            "rating": developer.rating,
            "reviews_count": developer.reviews_count,
            "is_verified": developer.is_verified,
            "verification_status": developer.verification_status,
            "properties_count": properties_count,
            "active_properties_count": active_properties_count,
            "created_at": developer.created_at,
            "updated_at": developer.updated_at,
        }

        return DeveloperResponse(**response_data)

    async def get_developers_list(
        self, db: AsyncSession, params: DeveloperSearchParams
    ) -> Tuple[List[DeveloperListResponse], int]:
        """
        Get list of developers with filtering and pagination.
        """
        # Build base query
        query = select(Developer)
        count_query = select(func.count(Developer.id))

        # Add filters
        conditions = []

        if params.is_verified is not None:
            conditions.append(Developer.is_verified == params.is_verified)

        if params.rating_min is not None:
            conditions.append(Developer.rating >= params.rating_min)

        if params.search:
            search_term = f"%{params.search}%"
            conditions.append(
                or_(
                    Developer.company_name.ilike(search_term),
                    Developer.legal_name.ilike(search_term),
                )
            )

        # Apply conditions
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Add pagination and ordering
        query = query.order_by(Developer.is_verified.desc(), Developer.rating.desc())
        query = query.offset((params.page - 1) * params.limit).limit(params.limit)

        # Execute query
        result = await db.execute(query)
        developers = result.scalars().all()

        # Get properties count for each developer
        developer_responses = []
        for developer in developers:
            properties_count_result = await db.execute(
                select(func.count(Property.id)).where(
                    Property.developer_id == developer.id
                )
            )
            properties_count = properties_count_result.scalar() or 0

            response_data = {
                "id": str(developer.id),
                "company_name": developer.company_name,
                "logo_url": developer.logo_url,
                "rating": developer.rating,
                "reviews_count": developer.reviews_count,
                "properties_count": properties_count,
                "is_verified": developer.is_verified,
                "verification_status": developer.verification_status,
                "description": developer.description,
            }
            developer_responses.append(DeveloperListResponse(**response_data))

        return developer_responses, total

    async def update_developer(
        self,
        db: AsyncSession,
        developer_id: str,
        request: DeveloperUpdateRequest,
        current_user: User,
    ) -> DeveloperResponse:
        """
        Update developer profile.
        Only the developer owner or admin can update.
        """
        # Get developer
        result = await db.execute(
            select(Developer)
            .options(selectinload(Developer.user))
            .where(Developer.id == developer_id)
        )
        developer = result.scalar_one_or_none()

        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
            )

        # Check permissions
        if current_user.role != UserRole.ADMIN and developer.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this developer profile",
            )

        # Update fields
        for field, value in request.dict(exclude_unset=True).items():
            setattr(developer, field, value)

        await db.commit()
        await db.refresh(developer)

        logger.info(
            "Developer profile updated: %s (ID: %s) by user %s",
            developer.company_name,
            developer.id,
            current_user.id,
        )

        return await self.get_developer_by_id(db, developer_id)

    async def verify_developer(
        self, db: AsyncSession, request: DeveloperVerificationRequest, admin_user: User
    ) -> DeveloperResponse:
        """
        Verify or reject developer (admin only).
        """
        if admin_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can verify developers",
            )

        # Get developer
        result = await db.execute(
            select(Developer).where(Developer.id == request.developer_id)
        )
        developer = result.scalar_one_or_none()

        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
            )

        # Update verification status
        developer.verification_status = request.verification_status
        developer.is_verified = (
            request.verification_status == VerificationStatus.APPROVED
        )

        await db.commit()

        logger.info(
            "Developer %s (ID: %s) verification status updated to %s by admin %s",
            developer.company_name,
            developer.id,
            request.verification_status,
            admin_user.id,
        )

        return await self.get_developer_by_id(db, request.developer_id)

    async def get_developer_by_user_id(
        self, db: AsyncSession, user_id: str
    ) -> Optional[DeveloperResponse]:
        """
        Get developer profile by user ID.
        """
        result = await db.execute(
            select(Developer)
            .options(selectinload(Developer.user))
            .where(Developer.user_id == user_id)
        )
        developer = result.scalar_one_or_none()

        if not developer:
            return None

        return await self.get_developer_by_id(db, developer.id)

    async def get_top_developers(
        self, db: AsyncSession, limit: int = 10
    ) -> List[DeveloperListResponse]:
        """
        Get top developers by rating and properties count.
        """
        query = (
            select(Developer)
            .where(Developer.is_verified == True)
            .order_by(Developer.rating.desc(), Developer.reviews_count.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        developers = result.scalars().all()

        # Add properties count
        developer_responses = []
        for developer in developers:
            properties_count_result = await db.execute(
                select(func.count(Property.id)).where(
                    Property.developer_id == developer.id
                )
            )
            properties_count = properties_count_result.scalar() or 0

            response_data = {
                "id": str(developer.id),
                "company_name": developer.company_name,
                "logo_url": developer.logo_url,
                "rating": developer.rating,
                "reviews_count": developer.reviews_count,
                "properties_count": properties_count,
                "is_verified": developer.is_verified,
                "verification_status": developer.verification_status,
                "description": developer.description,
            }
            developer_responses.append(DeveloperListResponse(**response_data))

        return developer_responses
