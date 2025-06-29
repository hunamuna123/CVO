"""
Booking API endpoints for property reservations and booking management.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.booking import (
    BookingCreateRequest,
    BookingListResponse,
    BookingResponse,
    BookingSearchParams,
    BookingSearchResponse,
    BookingStatusUpdateRequest,
    BookingUpdateRequest,
)
from app.services.booking_service import BookingService
from app.utils.security import (
    get_current_admin_user,
    get_current_developer_user,
    get_current_user,
)

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# Initialize the booking service
booking_service = BookingService()


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new booking",
    description="Create a new property booking/reservation",
)
async def create_booking(
    booking_data: BookingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Create a new property booking.

    **Requirements:**
    - Must be logged in
    - Valid access token in Authorization header

    **Request body:**
    - **property_id**: Property UUID to book
    - **contact_phone**: Contact phone number
    - **contact_email**: Contact email (optional)
    - **promo_code**: Promotional code (optional)
    - **notes**: Additional notes (optional)
    - **utm_source, utm_medium, utm_campaign**: Tracking parameters (optional)

    **Booking process:**
    1. Validates property availability
    2. Applies promotional codes if provided
    3. Calculates final price with discounts
    4. Creates booking with PENDING status
    5. Sets expiration time (typically 24-48 hours)
    6. Sends notifications to user and developer    

    **Platform commission:**
    - Automatically calculated based on platform settings
    - Typically 1-3% of the final price
    - Commission is charged to the developer
    """
    return await booking_service.create_booking(db, booking_data, str(current_user.id))


@router.get(
    "/",
    response_model=BookingSearchResponse,
    summary="Search bookings",
    description="Search bookings with filtering and pagination (admin only)",
)
async def search_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(
        None, description="Booking status (PENDING, CONFIRMED, PAID, CANCELLED, EXPIRED, COMPLETED)"
    ),
    source: Optional[str] = Query(
        None, description="Booking source (PLATFORM, DIRECT, PARTNER)"
    ),
    developer_id: Optional[str] = Query(None, description="Developer ID filter"),
    user_id: Optional[str] = Query(None, description="User ID filter"),
    property_id: Optional[str] = Query(None, description="Property ID filter"),
    date_from: Optional[str] = Query(None, description="Booking date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Booking date to (YYYY-MM-DD)"),
    price_from: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_to: Optional[float] = Query(None, ge=0, description="Maximum price"),
    promo_code: Optional[str] = Query(None, description="Used promo code"),
    sort: Optional[str] = Query(
        "created_desc", description="Sort by: created_desc, created_asc, price_desc, price_asc"
    ),
    search: Optional[str] = Query(None, description="Search in booking number, contact info"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> BookingSearchResponse:
    """
    Search bookings with advanced filtering (admin only).

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **status**: Filter by booking status
    - **source**: Filter by booking source
    - **developer_id**: Filter by developer
    - **user_id**: Filter by user
    - **property_id**: Filter by property
    - **date_from/to**: Date range filter
    - **price_from/to**: Price range filter
    - **promo_code**: Filter by used promo code
    - **sort**: Sorting option
    - **search**: Free text search

    Returns paginated booking results with full details.
    """
    search_params = BookingSearchParams(
        page=page,
        limit=limit,
        status=status,
        source=source,
        developer_id=developer_id,
        user_id=user_id,
        property_id=property_id,
        date_from=date_from,
        date_to=date_to,
        price_from=price_from,
        price_to=price_to,
        promo_code=promo_code,
        sort=sort,
        search=search,
    )

    return await booking_service.search_bookings(db, search_params)


@router.get(
    "/my",
    response_model=List[BookingListResponse],
    summary="Get my bookings",
    description="Get current user's bookings",
)
async def get_my_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[BookingListResponse]:
    """
    Get current user's bookings.

    **Query parameters:**
    - **page**: Page number
    - **limit**: Items per page
    - **status**: Filter by booking status

    Returns list of user's bookings with property information.
    """
    return await booking_service.get_user_bookings(
        db, str(current_user.id), page, limit, status
    )


@router.get(
    "/developer/{developer_id}",
    response_model=List[BookingListResponse],
    summary="Get developer bookings",
    description="Get bookings for developer's properties (developer/admin only)",
)
async def get_developer_bookings(
    developer_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[BookingListResponse]:
    """
    Get bookings for developer's properties.

    **Requirements:**
    - Must be the developer owner or admin
    - Valid access token in Authorization header

    **Path parameters:**
    - **developer_id**: Developer UUID

    **Query parameters:**
    - **page**: Page number
    - **limit**: Items per page
    - **status**: Filter by booking status

    Returns list of bookings for developer's properties.
    """
    # Check permissions
    if not current_user.is_admin:
        if not current_user.developer_profile or str(current_user.developer_profile.id) != developer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": "Доступ запрещен",
                        "details": {},
                    }
                },
            )

    return await booking_service.get_developer_bookings(
        db, developer_id, page, limit, status
    )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking details",
    description="Get detailed booking information",
)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Get detailed booking information by ID.

    **Requirements:**
    - Must be the booking owner, property developer, or admin
    - Valid access token in Authorization header

    **Path parameters:**
    - **booking_id**: Booking UUID

    Returns complete booking information including:
    - All booking details and status
    - Property information
    - User and developer information
    - Payment and pricing details
    - Tracking information
    """
    return await booking_service.get_booking_by_id(db, booking_id, str(current_user.id))


@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Update booking",
    description="Update booking information (owner only)",
)
async def update_booking(
    booking_id: str,
    booking_data: BookingUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Update booking information.

    **Requirements:**
    - Must be the booking owner
    - Booking must be in PENDING status
    - Valid access token in Authorization header

    **Updatable fields:**
    - Contact information (phone, email)
    - Notes
    - Promo code (if booking allows changes)

    **Note:** Some fields cannot be updated after confirmation.
    """
    return await booking_service.update_booking(
        db, booking_id, booking_data, str(current_user.id)
    )


@router.put(
    "/{booking_id}/status",
    response_model=BookingResponse,
    summary="Update booking status",
    description="Update booking status (developer/admin only)",
)
async def update_booking_status(
    booking_id: str,
    status_data: BookingStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Update booking status.

    **Requirements:**
    - Must be the property developer or admin
    - Valid access token in Authorization header

    **Available status transitions:**
    - **PENDING → CONFIRMED**: Developer confirms the booking
    - **CONFIRMED → PAID**: Payment is received
    - **PAID → COMPLETED**: Deal is completed
    - **Any status → CANCELLED**: Booking is cancelled

    **Status meanings:**
    - **PENDING**: Waiting for developer confirmation
    - **CONFIRMED**: Developer confirmed, waiting for payment
    - **PAID**: Payment received, proceeding with deal
    - **CANCELLED**: Booking cancelled by user or developer
    - **EXPIRED**: Booking expired (automatic)
    - **COMPLETED**: Deal completed successfully

    **Notes:**
    - Cancellation reason can be provided
    - Status changes trigger notifications
    - Some status changes may affect pricing
    """
    return await booking_service.update_booking_status(
        db, booking_id, status_data, str(current_user.id)
    )


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel booking",
    description="Cancel booking (owner only)",
)
async def cancel_booking(
    booking_id: str,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel booking.

    **Requirements:**
    - Must be the booking owner
    - Booking must be cancellable (PENDING or CONFIRMED status)
    - Valid access token in Authorization header

    **Query parameters:**
    - **reason**: Optional cancellation reason

    **Effects:**
    - Booking status changed to CANCELLED
    - Cancellation timestamp recorded
    - Notifications sent to relevant parties
    - Property becomes available again
    """
    await booking_service.cancel_booking(
        db, booking_id, str(current_user.id), reason
    )

    return {"message": "Booking cancelled successfully"}


@router.post(
    "/{booking_id}/confirm",
    response_model=BookingResponse,
    summary="Confirm booking (developer only)",
    description="Confirm booking by developer",
)
async def confirm_booking(
    booking_id: str,
    notes: Optional[str] = Query(None, description="Confirmation notes"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Confirm booking by developer.

    **Requirements:**
    - Must be the property developer
    - Booking must be in PENDING status
    - Valid access token in Authorization header

    **Query parameters:**
    - **notes**: Optional confirmation notes

    **Effects:**
    - Booking status changed to CONFIRMED
    - Confirmation timestamp recorded
    - User receives confirmation notification
    - Payment instructions may be sent
    """
    if not current_user.developer_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "NO_DEVELOPER_PROFILE",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await booking_service.confirm_booking(
        db, booking_id, str(current_user.developer_profile.id), notes
    )


@router.post(
    "/{booking_id}/mark-paid",
    response_model=BookingResponse,
    summary="Mark booking as paid (developer only)",
    description="Mark booking as paid by developer",
)
async def mark_booking_paid(
    booking_id: str,
    notes: Optional[str] = Query(None, description="Payment notes"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Mark booking as paid by developer.

    **Requirements:**
    - Must be the property developer
    - Booking must be in CONFIRMED status
    - Valid access token in Authorization header

    **Query parameters:**
    - **notes**: Optional payment notes

    **Effects:**
    - Booking status changed to PAID
    - Payment timestamp recorded
    - Platform commission calculated
    - Notifications sent
    """
    if not current_user.developer_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "NO_DEVELOPER_PROFILE",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await booking_service.mark_booking_paid(
        db, booking_id, str(current_user.developer_profile.id), notes
    )


@router.post(
    "/{booking_id}/complete",
    response_model=BookingResponse,
    summary="Complete booking (developer only)",
    description="Mark booking as completed by developer",
)
async def complete_booking(
    booking_id: str,
    notes: Optional[str] = Query(None, description="Completion notes"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:
    """
    Mark booking as completed by developer.

    **Requirements:**
    - Must be the property developer
    - Booking must be in PAID status
    - Valid access token in Authorization header

    **Query parameters:**
    - **notes**: Optional completion notes

    **Effects:**
    - Booking status changed to COMPLETED
    - Completion timestamp recorded
    - Property status may be updated
    - Final notifications sent
    - Platform commission finalized
    """
    if not current_user.developer_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "NO_DEVELOPER_PROFILE",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await booking_service.complete_booking(
        db, booking_id, str(current_user.developer_profile.id), notes
    )


@router.get(
    "/{booking_id}/analytics",
    response_model=dict,
    summary="Get booking analytics",
    description="Get analytics for a booking (developer/admin only)",
)
async def get_booking_analytics(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get analytics for a booking.

    **Requirements:**
    - Must be the property developer or admin
    - Valid access token in Authorization header

    **Analytics include:**
    - Booking timeline and status changes
    - Source and conversion tracking
    - Price breakdown and discounts
    - Communication history
    - Performance metrics
    """
    return await booking_service.get_booking_analytics(
        db, booking_id, str(current_user.id)
    )
