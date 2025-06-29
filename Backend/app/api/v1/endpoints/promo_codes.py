"""
Promo code API endpoints for promotional campaigns and discounts.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.promo_code import (
    PromoCodeCreateRequest,
    PromoCodeListResponse,
    PromoCodeResponse,
    PromoCodeSearchParams,
    PromoCodeSearchResponse,
    PromoCodeUpdateRequest,
    PromoCodeValidationRequest,
    PromoCodeValidationResponse,
)
from app.services.promo_code_service import PromoCodeService
from app.utils.security import (
    get_current_admin_user,
    get_current_developer_user,
    get_current_user,
)

router = APIRouter(prefix="/promo-codes", tags=["Promo Codes"])

# Initialize the promo code service
promo_code_service = PromoCodeService()


@router.post(
    "",
    response_model=PromoCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new promo code",
    description="Create a new promotional code (developer/admin only)",
)
async def create_promo_code(
    promo_code_data: PromoCodeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeResponse:
    """
    Create a new promotional code.

    **Requirements:**
    - Must be a developer (for developer-specific codes) or admin (for platform codes)
    - Valid access token in Authorization header

    **Request body:**
    - **code**: Unique promo code (e.g., "WELCOME2024")
    - **title**: Promotional title
    - **description**: Optional description
    - **promo_type**: PERCENTAGE, FIXED_AMOUNT, or CASHBACK
    - **discount_percentage**: For percentage discounts (0-100)
    - **discount_amount**: For fixed amount discounts
    - **max_discount_amount**: Maximum discount for percentage codes
    - **usage_limit**: Total usage limit (null for unlimited)
    - **usage_limit_per_user**: Usage limit per user (default: 1)
    - **min_order_amount**: Minimum order amount required
    - **valid_from/until**: Validity period
    - **for_new_users_only**: Only for new users
    - **target_property_id, target_complex_id**: Target specific property/complex
    - **target_city, target_region**: Geographic targeting

    **Promo code types:**
    - **PERCENTAGE**: Percentage discount (e.g., 5% off)
    - **FIXED_AMOUNT**: Fixed amount discount (e.g., 100,000 RUB off)
    - **CASHBACK**: Cashback after purchase

    **Targeting options:**
    - **Geographic**: Target specific city/region
    - **Property-specific**: Target specific property or complex
    - **User-specific**: Only for new users
    - **Amount-based**: Minimum order amount required
    """
    # Check permissions
    developer_id = None
    if not current_user.is_admin:
        if not current_user.developer_profile:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "NO_DEVELOPER_PROFILE",
                        "message": "Только застройщики и администраторы могут создавать промокоды",
                        "details": {},
                    }
                },
            )
        developer_id = str(current_user.developer_profile.id)

    return await promo_code_service.create_promo_code(db, promo_code_data, developer_id)


@router.get(
    "",
    response_model=PromoCodeSearchResponse,
    summary="Search promo codes",
    description="Search promotional codes with filtering (developer/admin only)",
)
async def search_promo_codes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    promo_type: Optional[str] = Query(
        None, description="Promo type (PERCENTAGE, FIXED_AMOUNT, CASHBACK)"
    ),
    status: Optional[str] = Query(
        None, description="Status (ACTIVE, INACTIVE, EXPIRED, USED_UP)"
    ),
    developer_id: Optional[str] = Query(None, description="Developer ID filter"),
    is_platform_code: Optional[bool] = Query(None, description="Platform codes only"),
    target_city: Optional[str] = Query(None, description="Target city filter"),
    target_region: Optional[str] = Query(None, description="Target region filter"),
    valid_only: Optional[bool] = Query(None, description="Only currently valid codes"),
    sort: Optional[str] = Query(
        "created_desc", description="Sort by: created_desc, created_asc, usage_desc, expiry_asc"
    ),
    search: Optional[str] = Query(None, description="Search in code, title, description"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeSearchResponse:
    """
    Search promotional codes with advanced filtering.

    **Requirements:**
    - Must be a developer (see own codes) or admin (see all codes)
    - Valid access token in Authorization header

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **promo_type**: Filter by promo type
    - **status**: Filter by status
    - **developer_id**: Filter by developer (admin only)
    - **is_platform_code**: Platform codes only
    - **target_city/region**: Geographic filters
    - **valid_only**: Only currently valid codes
    - **sort**: Sorting option
    - **search**: Free text search

    **Permissions:**
    - Developers see only their own codes
    - Admins see all codes (platform + developer codes)
    """
    # Check permissions and set developer filter
    if not current_user.is_admin and not current_user.developer_profile:
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

    # For non-admin users, filter by their developer ID
    if not current_user.is_admin:
        developer_id = str(current_user.developer_profile.id)

    search_params = PromoCodeSearchParams(
        page=page,
        limit=limit,
        promo_type=promo_type,
        status=status,
        developer_id=developer_id,
        is_platform_code=is_platform_code,
        target_city=target_city,
        target_region=target_region,
        valid_only=valid_only,
        sort=sort,
        search=search,
    )

    return await promo_code_service.search_promo_codes(db, search_params)


@router.get(
    "/public",
    response_model=List[PromoCodeListResponse],
    summary="Get public promo codes",
    description="Get publicly available promotional codes",
)
async def get_public_promo_codes(
    city: Optional[str] = Query(None, description="Filter by city"),
    region: Optional[str] = Query(None, description="Filter by region"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    limit: int = Query(10, ge=1, le=50, description="Number of codes to return"),
    db: AsyncSession = Depends(get_db),
) -> List[PromoCodeListResponse]:
    """
    Get publicly available promotional codes.

    **Query parameters:**
    - **city**: Filter by target city
    - **region**: Filter by target region
    - **property_type**: Filter by property type
    - **limit**: Number of codes to return

    Returns active promotional codes that are suitable for public display.
    Includes both platform codes and developer codes marked as public.
    """
    return await promo_code_service.get_public_promo_codes(
        db, city, region, property_type, limit
    )


@router.post(
    "/validate",
    response_model=PromoCodeValidationResponse,
    summary="Validate promo code",
    description="Validate promotional code for a specific order",
)
async def validate_promo_code(
    validation_data: PromoCodeValidationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeValidationResponse:
    """
    Validate promotional code for a specific order.

    **Requirements:**
    - Must be logged in
    - Valid access token in Authorization header

    **Request body:**
    - **code**: Promo code to validate
    - **property_id**: Property ID for the order
    - **order_amount**: Order amount to calculate discount

    **Validation checks:**
    - Code exists and is active
    - Code is currently valid (within date range)
    - Usage limits not exceeded
    - User eligibility (new user restrictions, etc.)
    - Geographic targeting matches
    - Property/complex targeting matches
    - Minimum order amount requirements

    **Response includes:**
    - **is_valid**: Whether the code is valid
    - **discount_amount**: Calculated discount amount
    - **final_amount**: Final amount after discount
    - **error_message**: Error message if invalid
    - **promo_details**: Promo code details if valid
    """
    return await promo_code_service.validate_promo_code(
        db, validation_data, str(current_user.id)
    )


@router.get(
    "/{promo_code_id}",
    response_model=PromoCodeResponse,
    summary="Get promo code details",
    description="Get detailed promo code information",
)
async def get_promo_code(
    promo_code_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeResponse:
    """
    Get detailed promo code information by ID.

    **Requirements:**
    - Must be the code owner (developer) or admin
    - Valid access token in Authorization header

    **Path parameters:**
    - **promo_code_id**: Promo code UUID

    Returns complete promo code information including:
    - All code details and settings
    - Usage statistics
    - Targeting information
    - Validity status
    """
    return await promo_code_service.get_promo_code_by_id(
        db, promo_code_id, str(current_user.id)
    )


@router.put(
    "/{promo_code_id}",
    response_model=PromoCodeResponse,
    summary="Update promo code",
    description="Update promo code information (owner/admin only)",
)
async def update_promo_code(
    promo_code_id: str,
    promo_code_data: PromoCodeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeResponse:
    """
    Update promo code information.

    **Requirements:**
    - Must be the code owner (developer) or admin
    - Valid access token in Authorization header

    **Updatable fields:**
    - Title and description
    - Usage limits
    - Validity dates (future dates only)
    - Targeting settings
    - Status (activate/deactivate)

    **Restrictions:**
    - Cannot change discount amount/type if already used
    - Cannot extend validity for expired codes
    - Some changes may require admin approval
    """
    return await promo_code_service.update_promo_code(
        db, promo_code_id, promo_code_data, str(current_user.id)
    )


@router.delete(
    "/{promo_code_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete promo code",
    description="Delete promo code (owner/admin only)",
)
async def delete_promo_code(
    promo_code_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete promo code.

    **Requirements:**
    - Must be the code owner (developer) or admin
    - Code must not have been used
    - Valid access token in Authorization header

    **Warning:** This action cannot be undone.
    Promo codes that have been used cannot be deleted for audit purposes.
    """
    await promo_code_service.delete_promo_code(
        db, promo_code_id, str(current_user.id)
    )

    return {"message": "Promo code deleted successfully"}


@router.post(
    "/{promo_code_id}/activate",
    response_model=PromoCodeResponse,
    summary="Activate promo code",
    description="Activate promo code (owner/admin only)",
)
async def activate_promo_code(
    promo_code_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeResponse:
    """
    Activate promo code.

    **Requirements:**
    - Must be the code owner (developer) or admin
    - Valid access token in Authorization header

    **Effects:**
    - Status changed to ACTIVE
    - Code becomes available for use
    - Public codes become visible in listings
    """
    return await promo_code_service.activate_promo_code(
        db, promo_code_id, str(current_user.id)
    )


@router.post(
    "/{promo_code_id}/deactivate",
    response_model=PromoCodeResponse,
    summary="Deactivate promo code",
    description="Deactivate promo code (owner/admin only)",
)
async def deactivate_promo_code(
    promo_code_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PromoCodeResponse:
    """
    Deactivate promo code.

    **Requirements:**
    - Must be the code owner (developer) or admin
    - Valid access token in Authorization header

    **Effects:**
    - Status changed to INACTIVE
    - Code becomes unavailable for new uses
    - Existing bookings with this code remain valid
    """
    return await promo_code_service.deactivate_promo_code(
        db, promo_code_id, str(current_user.id)
    )


@router.get(
    "/{promo_code_id}/analytics",
    response_model=dict,
    summary="Get promo code analytics",
    description="Get analytics for a promo code (owner/admin only)",
)
async def get_promo_code_analytics(
    promo_code_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get analytics for a promo code.

    **Requirements:**
    - Must be the code owner (developer) or admin
    - Valid access token in Authorization header

    **Analytics include:**
    - Usage statistics and trends
    - Conversion rates
    - Total discount amount given
    - Revenue impact
    - Popular properties/complexes
    - User demographics
    - Geographic distribution
    """
    return await promo_code_service.get_promo_code_analytics(
        db, promo_code_id, str(current_user.id), days
    )


@router.get(
    "/my/analytics",
    response_model=dict,
    summary="Get my promo codes analytics",
    description="Get analytics for developer's promo codes",
)
async def get_my_promo_codes_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get analytics for developer's promo codes.

    **Requirements:**
    - Must be a developer
    - Valid access token in Authorization header

    **Analytics include:**
    - Overall promo codes performance
    - Top performing codes
    - Usage trends over time
    - Total discounts given
    - Revenue impact
    - Conversion rates
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

    return await promo_code_service.get_developer_promo_codes_analytics(
        db, str(current_user.developer_profile.id), days
    )
