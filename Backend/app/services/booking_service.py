"""
Booking service for business logic related to property bookings.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Booking, Developer, Property, User
from app.models.booking import BookingStatus, BookingSource
from app.models.property import PropertyStatus
from app.schemas.booking import (
    BookingCreateRequest,
    BookingListResponse,
    BookingResponse,
    BookingSearchParams,
    BookingSearchResponse,
    BookingStatusUpdateRequest,
    BookingUpdateRequest,
    PropertyBasicInfo,
    UserBasicInfo,
    DeveloperBasicInfo,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class BookingService(BaseService):
    """Service for booking-related operations."""

    async def create_booking(
        self, db: AsyncSession, booking_data: BookingCreateRequest, user_id: str
    ) -> BookingResponse:
        """Create a new booking."""
        try:
            # Get user
            user_result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get property with developer info
            property_result = await db.execute(
                select(Property)
                .options(selectinload(Property.developer))
                .where(
                    Property.id == booking_data.property_id,
                    Property.status == PropertyStatus.ACTIVE
                )
            )
            property_obj = property_result.scalar_one_or_none()
            if not property_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Active property not found"
                )
            
            # Check if property is not already booked
            existing_booking = await db.execute(
                select(Booking).where(
                    Booking.property_id == booking_data.property_id,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.PAID])
                )
            )
            if existing_booking.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Property is already booked"
                )
            
            # Generate unique booking number
            booking_number = f"BK{datetime.now().strftime('%Y%m%d')}{str(uuid4())[:8].upper()}"
            
            # Calculate pricing
            property_price = property_obj.price
            discount_amount = Decimal("0.00")
            
            # Apply promo code if provided
            if booking_data.promo_code:
                # TODO: Implement promo code logic
                logger.info(f"Promo code {booking_data.promo_code} applied to booking")
            
            final_price = property_price - discount_amount
            
            # Platform commission (default 2%)
            platform_commission_rate = Decimal("0.02")
            platform_commission_amount = final_price * platform_commission_rate
            
            # Set expiration (48 hours from now)
            expires_at = datetime.utcnow() + timedelta(hours=48)
            
            # Create booking
            booking = Booking(
                user_id=user_id,
                property_id=booking_data.property_id,
                developer_id=property_obj.developer_id,
                booking_number=booking_number,
                status=BookingStatus.PENDING,
                source=BookingSource.PLATFORM,
                property_price=property_price,
                discount_amount=discount_amount,
                final_price=final_price,
                platform_commission_rate=platform_commission_rate,
                platform_commission_amount=platform_commission_amount,
                booking_date=datetime.utcnow(),
                expires_at=expires_at,
                contact_phone=booking_data.contact_phone,
                contact_email=booking_data.contact_email,
                notes=booking_data.notes,
                promo_code=booking_data.promo_code,
                utm_source=booking_data.utm_source,
                utm_medium=booking_data.utm_medium,
                utm_campaign=booking_data.utm_campaign,
            )
            
            db.add(booking)
            await db.commit()
            await db.refresh(booking)
            
            logger.info(
                f"Booking created: {booking_number} for property {property_obj.title} by user {user.phone}"
            )
            
            return await self._build_booking_response(db, booking)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create booking: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create booking"
            )

    async def search_bookings(
        self, db: AsyncSession, params: BookingSearchParams
    ) -> BookingSearchResponse:
        """Search bookings with filtering and pagination."""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.property_obj),
                selectinload(Booking.developer)
            )
        )
        
        conditions = []
        
        # Apply filters
        if params.status:
            conditions.append(Booking.status == params.status)
        if params.source:
            conditions.append(Booking.source == params.source)
        if params.developer_id:
            conditions.append(Booking.developer_id == params.developer_id)
        if params.user_id:
            conditions.append(Booking.user_id == params.user_id)
        if params.property_id:
            conditions.append(Booking.property_id == params.property_id)
        if params.promo_code:
            conditions.append(Booking.promo_code == params.promo_code)
        if params.price_from:
            conditions.append(Booking.final_price >= params.price_from)
        if params.price_to:
            conditions.append(Booking.final_price <= params.price_to)
        
        # Date filters
        if params.date_from:
            conditions.append(Booking.booking_date >= datetime.fromisoformat(params.date_from))
        if params.date_to:
            conditions.append(Booking.booking_date <= datetime.fromisoformat(params.date_to))
        
        # Search filter
        if params.search:
            search_term = f"%{params.search}%"
            conditions.append(
                or_(
                    Booking.booking_number.ilike(search_term),
                    Booking.contact_phone.ilike(search_term),
                    Booking.contact_email.ilike(search_term)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        if params.sort == "created_desc":
            query = query.order_by(desc(Booking.created_at))
        elif params.sort == "created_asc":
            query = query.order_by(Booking.created_at)
        elif params.sort == "price_desc":
            query = query.order_by(desc(Booking.final_price))
        elif params.sort == "price_asc":
            query = query.order_by(Booking.final_price)
        else:
            query = query.order_by(desc(Booking.created_at))
        
        # Apply pagination
        query = query.offset((params.page - 1) * params.limit).limit(params.limit)
        
        # Execute query
        result = await db.execute(query)
        bookings = result.scalars().all()
        
        # Build response items
        items = []
        for booking in bookings:
            booking_item = await self._build_booking_list_response(booking)
            items.append(booking_item)
        
        # Calculate pagination
        pages = (total + params.limit - 1) // params.limit
        has_next = params.page < pages
        has_prev = params.page > 1
        
        return BookingSearchResponse(
            items=items,
            total=total,
            page=params.page,
            limit=params.limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
            filters_applied={
                "status": params.status,
                "source": params.source,
                "developer_id": params.developer_id,
                "user_id": params.user_id,
                "property_id": params.property_id,
                "date_from": params.date_from,
                "date_to": params.date_to,
                "price_from": params.price_from,
                "price_to": params.price_to,
                "promo_code": params.promo_code,
            },
            sort_applied=params.sort,
            search_query=params.search,
        )

    async def get_user_bookings(
        self, db: AsyncSession, user_id: str, page: int, limit: int, status_filter: Optional[str]
    ) -> List[BookingListResponse]:
        """Get user bookings."""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.property_obj),
                selectinload(Booking.developer)
            )
            .where(Booking.user_id == user_id)
        )
        
        if status_filter:
            query = query.where(Booking.status == status_filter)
        
        query = (
            query.order_by(desc(Booking.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        
        result = await db.execute(query)
        bookings = result.scalars().all()
        
        results = []
        for booking in bookings:
            result = await self._build_booking_list_response(booking)
            results.append(result)
        return results

    async def get_developer_bookings(
        self, db: AsyncSession, developer_id: str, page: int, limit: int, status_filter: Optional[str]
    ) -> List[BookingListResponse]:
        """Get developer bookings."""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.property_obj),
                selectinload(Booking.developer)
            )
            .where(Booking.developer_id == developer_id)
        )
        
        if status_filter:
            query = query.where(Booking.status == status_filter)
        
        query = (
            query.order_by(desc(Booking.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        
        result = await db.execute(query)
        bookings = result.scalars().all()
        
        results = []
        for booking in bookings:
            result = await self._build_booking_list_response(booking)
            results.append(result)
        return results

    async def get_booking_by_id(
        self, db: AsyncSession, booking_id: str, user_id: str
    ) -> BookingResponse:
        """Get booking by ID with permission check."""
        result = await db.execute(
            select(Booking)
            .options(
                selectinload(Booking.user),
                selectinload(Booking.property_obj),
                selectinload(Booking.developer)
            )
            .where(Booking.id == booking_id)
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        # Check permissions: user owns booking, developer owns property, or is admin
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Permission check
        has_permission = (
            str(booking.user_id) == user_id or  # User owns booking
            str(booking.developer_id) == user_id or  # Developer owns property
            user.role.value == "ADMIN"  # Admin access
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return await self._build_booking_response(db, booking)

    async def update_booking(
        self, db: AsyncSession, booking_id: str, booking_data: BookingUpdateRequest, user_id: str
    ) -> BookingResponse:
        """Update booking (placeholder implementation)."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Обновление бронирования будет реализовано позже",
                    "details": {},
                }
            },
        )

    async def update_booking_status(
        self, db: AsyncSession, booking_id: str, status_data: BookingStatusUpdateRequest, user_id: str
    ) -> BookingResponse:
        """Update booking status (placeholder implementation)."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Обновление статуса бронирования будет реализовано позже",
                    "details": {},
                }
            },
        )

    async def cancel_booking(
        self, db: AsyncSession, booking_id: str, user_id: str, reason: Optional[str]
    ) -> None:
        """Cancel booking (placeholder implementation)."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Отмена бронирования будет реализована позже",
                    "details": {},
                }
            },
        )

    async def confirm_booking(
        self, db: AsyncSession, booking_id: str, developer_id: str, notes: Optional[str]
    ) -> BookingResponse:
        """Confirm booking by developer (placeholder implementation)."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Подтверждение бронирования будет реализовано позже",
                    "details": {},
                }
            },
        )

    async def mark_booking_paid(
        self, db: AsyncSession, booking_id: str, developer_id: str, notes: Optional[str]
    ) -> BookingResponse:
        """Mark booking as paid (placeholder implementation)."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Отметка об оплате будет реализована позже",
                    "details": {},
                }
            },
        )

    async def complete_booking(
        self, db: AsyncSession, booking_id: str, developer_id: str, notes: Optional[str]
    ) -> BookingResponse:
        """Complete booking (placeholder implementation)."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": {
                    "code": "NOT_IMPLEMENTED",
                    "message": "Завершение бронирования будет реализовано позже",
                    "details": {},
                }
            },
        )

    async def get_booking_analytics(
        self, db: AsyncSession, booking_id: str, user_id: str
    ) -> dict:
        """Get booking analytics (placeholder implementation)."""
        return {
            "message": "Аналитика бронирования будет реализована позже",
            "booking_id": booking_id,
        }
    
    async def _build_booking_response(self, db: AsyncSession, booking: Booking) -> BookingResponse:
        """Build detailed booking response."""
        # Get related objects if not loaded
        if not hasattr(booking, 'user') or booking.user is None:
            await db.refresh(booking, ['user', 'property_obj', 'developer'])
        
        return BookingResponse(
            id=booking.id,
            booking_number=booking.booking_number,
            status=booking.status,
            source=booking.source,
            property_price=booking.property_price,
            discount_amount=booking.discount_amount,
            final_price=booking.final_price,
            property=self._build_property_basic_info(booking.property_obj),
            user=self._build_user_basic_info(booking.user),
            developer=self._build_developer_basic_info(booking.developer),
            booking_date=booking.booking_date,
            expires_at=booking.expires_at,
            confirmed_at=booking.confirmed_at,
            contact_phone=booking.contact_phone,
            contact_email=booking.contact_email,
            platform_commission_rate=booking.platform_commission_rate,
            platform_commission_amount=booking.platform_commission_amount,
            paid_at=booking.paid_at,
            cancelled_at=booking.cancelled_at,
            completed_at=booking.completed_at,
            notes=booking.notes,
            cancellation_reason=booking.cancellation_reason,
            promo_code=booking.promo_code,
            utm_source=booking.utm_source,
            utm_medium=booking.utm_medium,
            utm_campaign=booking.utm_campaign,
            is_active=booking.is_active,
            is_expired=booking.is_expired,
            discount_percentage=booking.discount_percentage,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )
    
    async def _build_booking_list_response(self, booking: Booking) -> BookingListResponse:
        """Build booking list response."""
        return BookingListResponse(
            id=booking.id,
            booking_number=booking.booking_number,
            status=booking.status,
            source=booking.source,
            property_price=booking.property_price,
            discount_amount=booking.discount_amount,
            final_price=booking.final_price,
            property=self._build_property_basic_info(booking.property_obj),
            user=self._build_user_basic_info(booking.user),
            developer=self._build_developer_basic_info(booking.developer),
            booking_date=booking.booking_date,
            expires_at=booking.expires_at,
            confirmed_at=booking.confirmed_at,
            contact_phone=booking.contact_phone,
            contact_email=booking.contact_email,
        )
    
    def _build_property_basic_info(self, property_obj: Property) -> PropertyBasicInfo:
        """Build property basic info."""
        # Safely get main image URL without triggering lazy loading
        main_image_url = None
        try:
            # Check if images are already loaded
            if hasattr(property_obj, 'images') and property_obj.images:
                for image in property_obj.images:
                    if getattr(image, 'is_main', False):
                        main_image_url = getattr(image, 'url', None)
                        break
                if not main_image_url and property_obj.images:
                    # Fallback to first image if no main image
                    main_image_url = getattr(property_obj.images[0], 'url', None)
        except Exception:
            # If we can't access images safely, just set to None
            main_image_url = None
        
        return PropertyBasicInfo(
            id=property_obj.id,
            title=property_obj.title,
            property_type=property_obj.property_type.value,
            deal_type=property_obj.deal_type.value,
            price=property_obj.price,
            full_address=property_obj.full_address,
            main_image_url=main_image_url,
        )
    
    def _build_user_basic_info(self, user: User) -> UserBasicInfo:
        """Build user basic info."""
        full_name = f"{user.first_name} {user.last_name}"
        if user.middle_name:
            full_name = f"{user.first_name} {user.middle_name} {user.last_name}"
        
        return UserBasicInfo(
            id=user.id,
            full_name=full_name.strip(),
            phone=user.phone,
            email=user.email,
        )
    
    def _build_developer_basic_info(self, developer: Developer) -> DeveloperBasicInfo:
        """Build developer basic info."""
        return DeveloperBasicInfo(
            id=developer.id,
            company_name=developer.company_name,
            contact_phone=developer.contact_phone,
            contact_email=developer.contact_email,
            is_verified=developer.is_verified,
        )
