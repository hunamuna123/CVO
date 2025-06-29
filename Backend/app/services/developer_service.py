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
from app.models.complex import Complex
from app.models.developer import VerificationStatus
from app.schemas.auth import AuthResponse
from app.schemas.developer import (
    DeveloperDashboardResponse,
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

    async def get_all_developers(
        self, db: AsyncSession
    ) -> List[DeveloperListResponse]:
        """
        Get all developers without pagination.
        
        Simple method to retrieve all developers for UI components
        like select lists, dropdowns, etc.
        """
        try:
            # Get all developers with basic info
            query = (
                select(Developer)
                .where(Developer.is_verified == True)  # Only verified developers
                .order_by(Developer.company_name.asc())
            )
            
            result = await db.execute(query)
            developers = result.scalars().all()
            
            # Convert to response format
            developer_list = []
            for developer in developers:
                # Get properties count for each developer
                properties_count_result = await db.execute(
                    select(func.count(Property.id)).where(
                        and_(
                            Property.developer_id == developer.id,
                            Property.status == PropertyStatus.ACTIVE,
                        )
                    )
                )
                properties_count = properties_count_result.scalar() or 0
                
                developer_response = DeveloperListResponse(
                    id=str(developer.id),
                    company_name=developer.company_name,
                    logo_url=developer.logo_url,
                    rating=developer.rating,
                    reviews_count=developer.reviews_count,
                    is_verified=developer.is_verified,
                    verification_status=developer.verification_status,
                    description=developer.description,
                    properties_count=properties_count,
                )
                developer_list.append(developer_response)
            
            logger.info("Retrieved all developers", count=len(developer_list))
            return developer_list
            
        except Exception as e:
            logger.error(
                "Failed to get all developers: %s",
                str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "ALL_DEVELOPERS_RETRIEVAL_FAILED",
                        "message": "Не удалось получить список всех застройщиков",
                        "details": {"error": str(e)},
                    }
                },
            )

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
    
    async def get_public_developers_list(
        self, db: AsyncSession, params: DeveloperSearchParams
    ) -> tuple[List[DeveloperListResponse], int]:
        """
        Get paginated list of public (verified) developers.
        """
        # Force verified filter for public access
        params.is_verified = True
        return await self.get_developers_list(db, params)
    
    async def get_developer_dashboard_stats(
        self, db: AsyncSession, developer_id: str
    ) -> DeveloperDashboardResponse:
        """
        Get dashboard statistics for developer.
        """
        # Get basic counts
        total_properties_result = await db.execute(
            select(func.count(Property.id)).where(Property.developer_id == developer_id)
        )
        total_properties = total_properties_result.scalar() or 0
        
        # For now, return basic stats. TODO: Implement full dashboard logic
        return DeveloperDashboardResponse(
            total_properties=total_properties,
            active_properties=total_properties,  # Simplified
            total_complexes=0,  # TODO: Implement when complex model is available
            total_views=0,
            total_contacts=0,
            total_bookings=0,
            monthly_views=0,
            monthly_contacts=0,
            monthly_bookings=0,
        )
    
    async def get_developer_detailed_statistics(
        self, db: AsyncSession, developer_id: str, period: str
    ) -> dict:
        """
        Get detailed statistics for developer.
        """
        # TODO: Implement detailed statistics
        return {
            "period": period,
            "properties_stats": {},
            "views_stats": {},
            "engagement_stats": {},
            "revenue_stats": {},
            "booking_stats": {},
            "performance_metrics": {},
            "charts_data": {},
        }
    
    async def get_developer_properties(
        self, db: AsyncSession, developer_id: str, page: int, limit: int,
        status: Optional[str] = None, property_type: Optional[str] = None,
        city: Optional[str] = None, search: Optional[str] = None
    ) -> dict:
        """
        Get properties for developer with filtering.
        """
        query = select(Property).where(Property.developer_id == developer_id)
        
        # Apply filters
        if status:
            # TODO: Implement when status field is available
            pass
        if property_type:
            # TODO: Implement when property_type field is available
            pass
        if city:
            # TODO: Implement city filtering
            pass
        if search:
            # TODO: Implement search in title/address
            pass
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset((page - 1) * limit).limit(limit)
        
        result = await db.execute(query)
        properties = result.scalars().all()
        
        # Convert properties to serializable format
        property_items = []
        for prop in properties:
            property_data = {
                "id": str(prop.id),
                "title": getattr(prop, 'title', ''),
                "price": getattr(prop, 'price', 0),
                "address": getattr(prop, 'address', ''),
                "area": getattr(prop, 'area', 0),
                "rooms": getattr(prop, 'rooms', 0),
                "floor": getattr(prop, 'floor', 0),
                "total_floors": getattr(prop, 'total_floors', 0),
                "status": getattr(prop, 'status', '').value if hasattr(getattr(prop, 'status', ''), 'value') else str(getattr(prop, 'status', '')),
                "created_at": prop.created_at.isoformat() if prop.created_at else None,
                "updated_at": prop.updated_at.isoformat() if prop.updated_at else None,
            }
            property_items.append(property_data)
        
        return {
            "items": property_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
        }
    
    async def get_developer_complexes(
        self, db: AsyncSession, developer_id: str, page: int, limit: int,
        status: Optional[str] = None, city: Optional[str] = None,
        search: Optional[str] = None
    ) -> dict:
        """
        Get complexes for developer with filtering.
        """
        # TODO: Implement when Complex model is available
        return {
            "items": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0,
            },
        }
    
    async def get_public_developer_properties(
        self, db: AsyncSession, developer_id: str, page: int, limit: int,
        property_type: Optional[str] = None, city: Optional[str] = None,
        price_min: Optional[int] = None, price_max: Optional[int] = None
    ) -> dict:
        """
        Get public properties for developer.
        """
        # Verify developer is verified first
        result = await db.execute(
            select(Developer).where(
                Developer.id == developer_id,
                Developer.is_verified == True
            )
        )
        developer = result.scalar_one_or_none()
        
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verified developer not found"
            )
        
        query = select(Property).where(Property.developer_id == developer_id)
        
        # Apply filters
        if property_type:
            # TODO: Implement when property_type field is available
            pass
        if city:
            # TODO: Implement city filtering
            pass
        if price_min:
            query = query.where(Property.price >= price_min)
        if price_max:
            query = query.where(Property.price <= price_max)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        query = query.offset((page - 1) * limit).limit(limit)
        
        result = await db.execute(query)
        properties = result.scalars().all()
        
        # Convert properties to serializable format
        property_items = []
        for prop in properties:
            property_data = {
                "id": str(prop.id),
                "title": getattr(prop, 'title', ''),
                "price": getattr(prop, 'price', 0),
                "address": getattr(prop, 'address', ''),
                "area": getattr(prop, 'area', 0),
                "rooms": getattr(prop, 'rooms', 0),
                "floor": getattr(prop, 'floor', 0),
                "total_floors": getattr(prop, 'total_floors', 0),
                "status": getattr(prop, 'status', '').value if hasattr(getattr(prop, 'status', ''), 'value') else str(getattr(prop, 'status', '')),
                "created_at": prop.created_at.isoformat() if prop.created_at else None,
                "updated_at": prop.updated_at.isoformat() if prop.updated_at else None,
            }
            property_items.append(property_data)
        
        return {
            "items": property_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
            "developer": {
                "id": str(developer.id),
                "company_name": developer.company_name,
                "logo_url": developer.logo_url,
            },
        }
    
    async def get_public_developer_complexes(
        self, db: AsyncSession, developer_id: str, page: int, limit: int,
        city: Optional[str] = None, status: Optional[str] = None
    ) -> dict:
        """
        Get public complexes for developer.
        """
        # Verify developer is verified first
        result = await db.execute(
            select(Developer).where(
                Developer.id == developer_id,
                Developer.is_verified == True
            )
        )
        developer = result.scalar_one_or_none()
        
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verified developer not found"
            )
        
        # Get complexes for developer
        query = select(Complex).where(Complex.developer_id == developer_id)

        # Apply filters
        if city:
            query = query.where(Complex.city == city)

        if status:
            query = query.where(Complex.status == status)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.offset((page - 1) * limit).limit(limit)

        result = await db.execute(query)
        complexes = result.scalars().all()

        # Convert complexes to serializable format
        complex_items = []
        for complex_obj in complexes:
            complex_data = {
                "id": str(complex_obj.id),
                "name": complex_obj.name,
                "status": complex_obj.status.name,
                "city": complex_obj.city,
                "address": complex_obj.address,
                "construction_start_date": complex_obj.construction_start_date.isoformat() if complex_obj.construction_start_date else None,
                "planned_completion_date": complex_obj.planned_completion_date.isoformat() if complex_obj.planned_completion_date else None,
                "actual_completion_date": complex_obj.actual_completion_date.isoformat() if complex_obj.actual_completion_date else None,
                "price_from": float(complex_obj.price_from) if complex_obj.price_from else None,
                "price_to": float(complex_obj.price_to) if complex_obj.price_to else None,
            }
            complex_items.append(complex_data)
        
        return {
            "items": complex_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
            "developer": {
                "id": str(developer.id),
                "company_name": developer.company_name,
                "logo_url": developer.logo_url,
            },
        }
    
    async def login_developer(
        self, db: AsyncSession, request
    ):
        """
        Developer login method.
        TODO: Implement developer-specific login logic.
        """
        # TODO: Implement developer login
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Developer login not implemented yet"
        )
    
    async def logout_developer(
        self, db: AsyncSession, user_id: str
    ):
        """
        Developer logout method.
        TODO: Implement developer-specific logout logic.
        """
        # TODO: Implement developer logout
        pass
    
    async def change_password(
        self, db: AsyncSession, user_id: str, request
    ):
        """
        Change developer password.
        TODO: Implement password change logic.
        """
        # TODO: Implement password change
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Password change not implemented yet"
        )
    
    async def get_pending_developers(
        self, db: AsyncSession
    ) -> List[DeveloperResponse]:
        """
        Get all developers pending verification.
        """
        query = (
            select(Developer)
            .where(Developer.verification_status == VerificationStatus.PENDING)
            .order_by(Developer.created_at.asc())
        )
        
        result = await db.execute(query)
        developers = result.scalars().all()
        
        # Convert to response format
        responses = []
        for developer in developers:
            response = await self.get_developer_by_id(db, str(developer.id))
            responses.append(response)
        
        return responses
    
    async def delete_developer(
        self, db: AsyncSession, developer_id: str, admin_user: User
    ):
        """
        Delete developer account (admin only).
        """
        if admin_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete developers"
            )
        
        # Get developer
        result = await db.execute(
            select(Developer).where(Developer.id == developer_id)
        )
        developer = result.scalar_one_or_none()
        
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Developer not found"
            )
        
        # TODO: Handle cascading deletes properly
        await db.delete(developer)
        await db.commit()
        
        logger.info(
            "Developer %s (ID: %s) deleted by admin %s",
            developer.company_name,
            developer.id,
            admin_user.id,
        )
    
    async def admin_register_developer(
        self, db: AsyncSession, request: DeveloperRegisterRequest, admin_user: User
    ) -> DeveloperResponse:
        """
        Register developer directly without phone verification (admin only).
        """
        if admin_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can register developers directly"
            )
        
        # TODO: Implement admin registration logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Admin developer registration not implemented yet"
        )
    
    async def submit_verification_request(
        self, db: AsyncSession, developer_id: str, documents: List[str], notes: Optional[str]
    ) -> dict:
        """
        Submit verification request with documents.
        """
        # TODO: Implement verification request submission
        return {
            "message": "Verification request submitted successfully",
            "developer_id": developer_id,
            "documents_count": len(documents),
        }
