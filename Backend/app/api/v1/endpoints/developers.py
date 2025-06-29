"""
Developer API endpoints for registration, management, and verification.
"""

import structlog
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.auth import AuthResponse
from app.schemas.developer import DeveloperLoginRequest as LoginRequest, DeveloperPasswordChangeRequest as PasswordChangeRequest
from app.schemas.developer import (
    DeveloperDashboardResponse,
    DeveloperStatsResponse,
    DeveloperListPaginated,
    DeveloperListResponse,
    DeveloperRegisterRequest,
    DeveloperResponse,
    DeveloperSearchParams,
    DeveloperUpdateRequest,
    DeveloperVerificationRequest,
    PaginationMeta,
)
from app.services.developer_service import DeveloperService
from app.utils.security import (
    get_current_admin_user,
    get_current_developer_user,
    get_current_user,
)

router = APIRouter(prefix="/developers", tags=["Developers"])

# Initialize the developer service
developer_service = DeveloperService()
logger = structlog.get_logger(__name__)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Register new developer company",
    description="Register a new real estate developer company with full legal information",
)
async def register_developer(
    request: DeveloperRegisterRequest, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Register a new developer company.

    This endpoint creates both a User account (with DEVELOPER role) and a Developer profile.

    **Required fields:**
    - **phone**: Company contact phone (+7XXXXXXXXXX)
    - **email**: Company contact email
    - **first_name**: Contact person first name
    - **last_name**: Contact person last name
    - **company_name**: Company brand name (e.g., "ПИК")
    - **legal_name**: Full legal company name
    - **inn**: INN (Tax ID) - 10 or 12 digits
    - **ogrn**: OGRN - 13 or 15 digits
    - **legal_address**: Complete legal address
    - **contact_phone**: Company contact phone
    - **contact_email**: Company contact email

    **Optional fields:**
    - **middle_name**: Contact person middle name
    - **website**: Company website URL
    - **description**: Company description

    Returns session_id for SMS verification.
    """
    return await developer_service.register_developer(db, request)


@router.get(
    "/all",
    response_model=List[DeveloperListResponse],
    summary="Get all developers",
    description="Get all developers without pagination (for simple listings)",
    responses={
        200: {
            "description": "List of all verified developers",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "company_name": "ПИК",
                            "logo_url": "https://example.com/logo.png",
                            "rating": 4.8,
                            "reviews_count": 156,
                            "properties_count": 89,
                            "is_verified": True,
                            "verification_status": "APPROVED",
                            "description": "Крупнейший девелопер России"
                        }
                    ]
                }
            }
        }
    }
)
async def get_all_developers(
    db: AsyncSession = Depends(get_db),
) -> List[DeveloperListResponse]:
    """
    Get all developers without pagination.
    
    **Use cases:**
    - Dropdown lists in property creation forms
    - Select lists for filtering
    - Small UI components that need the full list
    
    **Returns:**
    - All verified developers with basic information
    - Sorted alphabetically by company name
    - Only active and verified developers included
    
    **Performance note:**
    - This endpoint returns all developers at once
    - For large datasets, consider using the paginated endpoint instead
    """
    try:
        developers = await developer_service.get_all_developers(db)
        return developers
    except Exception as e:
        logger.error("Failed to get all developers: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "DEVELOPERS_RETRIEVAL_FAILED",
                    "message": "Не удалось получить список застройщиков",
                    "details": {"error": str(e)},
                }
            },
        )


@router.get(
    "/",
    response_model=DeveloperListPaginated,
    summary="Get developers list",
    description="Get paginated list of developers with filtering and search",
    responses={
        200: {
            "description": "Paginated list of developers",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "company_name": "ПИК",
                                "logo_url": "https://example.com/logo.png",
                                "rating": 4.8,
                                "reviews_count": 156,
                                "properties_count": 89,
                                "is_verified": True,
                                "verification_status": "APPROVED",
                                "description": "Крупнейший девелопер России"
                            }
                        ],
                        "pagination": {
                            "page": 1,
                            "limit": 20,
                            "total": 156,
                            "pages": 8,
                            "has_next": True,
                            "has_prev": False,
                            "next_page": 2,
                            "prev_page": None
                        }
                    }
                }
            }
        }
    }
)
async def get_developers(
    page: int = Query(1, ge=1, description="Page number for pagination", example=1),
    limit: int = Query(6, ge=1, le=100, description="Number of items per page (max 100)", example=20),
    city: Optional[str] = Query(None, description="Filter developers by city", example="Москва"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status", example=True),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating filter (0-5)", example=4.0),
    search: Optional[str] = Query(None, description="Search in company name", example="ПИК"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of developers with filtering and search.

    **Query parameters (all optional):**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **city**: Filter developers by city name
    - **is_verified**: Show only verified (true) or unverified (false) developers
    - **rating_min**: Minimum rating threshold (0-5 scale)
    - **search**: Free text search in company names

    **Response format:**
    - **items**: Array of developer objects with detailed information
    - **pagination**: Pagination metadata including page info and navigation

    **Filtering logic:**
    - All filters can be combined
    - Search is case-insensitive and matches partial company names
    - Results are sorted by verification status first, then by rating

    **Use cases:**
    - Developer directory with search and filtering
    - Admin panels for developer management
    - Partner listings with pagination
    """
    params = DeveloperSearchParams(
        page=page,
        limit=limit,
        city=city,
        is_verified=is_verified,
        rating_min=rating_min,
        search=search,
    )

    developers, total = await developer_service.get_developers_list(db, params)

    # Calculate pagination metadata
    pages = (total + limit - 1) // limit
    has_next = page < pages
    has_prev = page > 1
    
    pagination = PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=page + 1 if has_next else None,
        prev_page=page - 1 if has_prev else None
    )
    
    return DeveloperListPaginated(
        items=developers,
        pagination=pagination
    )


@router.get(
    "/top",
    response_model=List[DeveloperListResponse],
    summary="Get top developers",
    description="Get top-rated verified developers",
)
async def get_top_developers(
    limit: int = Query(10, ge=1, le=50, description="Number of developers to return"),
    db: AsyncSession = Depends(get_db),
) -> List[DeveloperListResponse]:
    """
    Get top developers by rating and activity.

    Returns top-rated and most active verified developers.
    Perfect for homepage or featured developers section.
    """
    return await developer_service.get_top_developers(db, limit)


@router.get(
    "/{developer_id}",
    response_model=DeveloperResponse,
    summary="Get developer by ID",
    description="Get detailed developer information by ID",
)
async def get_developer(
    developer_id: str, db: AsyncSession = Depends(get_db)
) -> DeveloperResponse:
    """
    Get detailed developer information by ID.

    **Path parameters:**
    - **developer_id**: Developer UUID

    Returns complete developer information including:
    - Company details and legal information
    - Contact information
    - Rating and reviews statistics
    - Properties count and verification status
    """
    return await developer_service.get_developer_by_id(db, developer_id)


@router.put(
    "/{developer_id}",
    response_model=DeveloperResponse,
    summary="Update developer profile",
    description="Update developer profile (owner or admin only)",
)
async def update_developer(
    developer_id: str,
    request: DeveloperUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DeveloperResponse:
    """
    Update developer profile.

    **Requirements:**
    - Must be the developer owner or admin
    - Valid access token in Authorization header

    **Updatable fields:**
    - **company_name**: Company brand name
    - **contact_phone**: Company contact phone
    - **contact_email**: Company contact email
    - **website**: Company website URL
    - **description**: Company description

    **Note:** Legal information (INN, OGRN, legal_name, legal_address) cannot be updated
    and requires admin verification for changes.
    """
    return await developer_service.update_developer(
        db, developer_id, request, current_user
    )


@router.post(
    "/verify",
    response_model=DeveloperResponse,
    summary="Verify developer (admin only)",
    description="Approve or reject developer verification (admin only)",
)
async def verify_developer(
    request: DeveloperVerificationRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> DeveloperResponse:
    """
    Verify or reject developer (admin only).

    **Requirements:**
    - Must be an admin user
    - Valid admin access token in Authorization header

    **Request body:**
    - **developer_id**: Developer UUID to verify
    - **verification_status**: APPROVED, REJECTED, or PENDING
    - **notes**: Optional verification notes

    **Verification process:**
    - PENDING: Initial status, under review
    - APPROVED: Developer is verified and can post properties
    - REJECTED: Developer verification failed, cannot post properties
    """
    return await developer_service.verify_developer(db, request, admin_user)


@router.get(
    "/me/profile",
    response_model=DeveloperResponse,
    summary="Get my developer profile",
    description="Get current user's developer profile",
)
async def get_my_developer_profile(
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> DeveloperResponse:
    """
    Get current user's developer profile.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    Returns the developer profile associated with the current user.
    If the user doesn't have a developer profile, returns 404.
    """
    developer_profile = await developer_service.get_developer_by_user_id(
        db, str(current_user.id)
    )

    if not developer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEVELOPER_PROFILE_NOT_FOUND",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return developer_profile


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Developer login",
    description="Authenticate developer with email and password",
)
async def login_developer(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate developer with email and password.

    **Request body:**
    - **email**: Developer email address
    - **password**: Developer password

    **Returns:**
    - **access_token**: JWT token for authenticated requests
    - **refresh_token**: Token for refreshing access token
    - **token_type**: Always "Bearer"
    - **expires_in**: Token expiration time in seconds
    - **user**: User profile information

    **Error responses:**
    - **401**: Invalid credentials
    - **403**: Account not verified or inactive
    - **404**: User not found
    """
    return await developer_service.login_developer(db, request)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Developer logout",
    description="Logout developer and invalidate tokens",
)
async def logout_developer(
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Logout developer and invalidate all tokens.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    This endpoint invalidates all tokens for the current developer user,
    requiring them to login again for future requests.
    """
    await developer_service.logout_developer(db, str(current_user.id))


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change developer password",
    description="Change password for authenticated developer",
)
async def change_developer_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Change password for authenticated developer.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    **Request body:**
    - **current_password**: Current password
    - **new_password**: New password (min 8 characters)
    - **confirm_password**: Confirmation of new password

    **Validation:**
    - Current password must be correct
    - New password must meet security requirements
    - New password and confirmation must match
    """
    await developer_service.change_password(db, str(current_user.id), request)
    return {"message": "Пароль успешно изменен"}


@router.put(
    "/me/profile",
    response_model=DeveloperResponse,
    summary="Update my developer profile",
    description="Update current user's developer profile",
)
async def update_my_developer_profile(
    request: DeveloperUpdateRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> DeveloperResponse:
    """
    Update current user's developer profile.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    **Updatable fields:**
    - **company_name**: Company brand name
    - **contact_phone**: Company contact phone
    - **contact_email**: Company contact email
    - **website**: Company website URL
    - **description**: Company description

    **Note:** Legal information (INN, OGRN, legal_name, legal_address) cannot be updated
    and requires admin verification for changes.
    """
    # Get developer profile first
    developer_profile = await developer_service.get_developer_by_user_id(
        db, str(current_user.id)
    )

    if not developer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEVELOPER_PROFILE_NOT_FOUND",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await developer_service.update_developer(
        db, str(developer_profile.id), request, current_user
    )


@router.get(
    "/me/dashboard",
    response_model=DeveloperDashboardResponse,
    summary="Get developer dashboard data",
    description="Get dashboard statistics for current developer",
)
async def get_developer_dashboard(
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> DeveloperDashboardResponse:
    """
    Get dashboard statistics for current developer.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    **Returns:**
    - **total_properties**: Total number of properties
    - **active_properties**: Currently active properties
    - **sold_properties**: Properties marked as sold
    - **total_complexes**: Total number of complexes
    - **active_complexes**: Currently active complexes
    - **total_views**: Total property views
    - **total_inquiries**: Total inquiries received
    - **monthly_views**: Views in current month
    - **monthly_inquiries**: Inquiries in current month
    - **avg_rating**: Average rating from reviews
    - **total_reviews**: Total number of reviews
    - **verification_status**: Current verification status
    - **recent_activities**: Recent activity items

    **Use cases:**
    - Developer dashboard main page
    - Performance overview
    - Business analytics
    """
    # Get developer profile first
    developer_profile = await developer_service.get_developer_by_user_id(
        db, str(current_user.id)
    )

    if not developer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEVELOPER_PROFILE_NOT_FOUND",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await developer_service.get_developer_dashboard_stats(
        db, str(developer_profile.id)
    )


@router.get(
    "/me/statistics",
    response_model=dict,
    summary="Get detailed developer statistics",
    description="Get detailed analytics and statistics for current developer",
)
async def get_developer_statistics(
    period: Optional[str] = Query(
        "month", 
        description="Statistics period: 'week', 'month', 'quarter', 'year'",
        regex="^(week|month|quarter|year)$"
    ),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get detailed analytics and statistics for current developer.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    **Query parameters:**
    - **period**: Statistics period (week, month, quarter, year)

    **Returns detailed analytics:**
    - **views_analytics**: Views breakdown by time period
    - **inquiries_analytics**: Inquiries statistics and trends
    - **properties_performance**: Individual property performance metrics
    - **conversion_metrics**: Lead conversion rates
    - **geographic_distribution**: Properties distribution by location
    - **price_analytics**: Pricing trends and comparisons
    - **market_position**: Position relative to competitors

    **Use cases:**
    - Detailed analytics dashboard
    - Business intelligence reports
    - Performance optimization insights
    """
    # Get developer profile first
    developer_profile = await developer_service.get_developer_by_user_id(
        db, str(current_user.id)
    )

    if not developer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEVELOPER_PROFILE_NOT_FOUND",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await developer_service.get_developer_detailed_statistics(
        db, str(developer_profile.id), period
    )


# Admin-only endpoint for developer registration without phone verification
@router.post(
    "/admin/register",
    response_model=DeveloperResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Admin: Register developer without verification",
    description="Register a new developer company directly without phone verification (admin only)",
)
async def admin_register_developer(
    request: DeveloperRegisterRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> DeveloperResponse:
    """
    Register a new developer company directly without phone verification (admin only).

    **Requirements:**
    - Must be an admin user
    - Valid admin access token in Authorization header

    **Differences from regular registration:**
    - No SMS verification required
    - Account is activated immediately
    - Verification status can be set to APPROVED directly
    - Password is auto-generated and returned

    **Use cases:**
    - Bulk developer onboarding
    - Migration from external systems
    - Manual developer registration by support team
    """
    return await developer_service.admin_register_developer(db, request, admin_user)


# Admin-only endpoints for developer management
@router.get(
    "/admin/pending",
    response_model=List[DeveloperResponse],
    summary="Admin: Get pending verification developers",
    description="Get all developers pending verification (admin only)",
)
async def get_pending_developers(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> List[DeveloperResponse]:
    """
    Get all developers pending verification (admin only).

    **Requirements:**
    - Must be an admin user
    - Valid admin access token in Authorization header

    **Returns:**
    - List of developers with PENDING verification status
    - Sorted by registration date (oldest first)
    - Includes all developer details for review

    **Use cases:**
    - Admin verification queue
    - Pending applications review
    - Verification workflow management
    """
    return await developer_service.get_pending_developers(db)


@router.delete(
    "/admin/{developer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Admin: Delete developer",
    description="Permanently delete developer account (admin only)",
)
async def admin_delete_developer(
    developer_id: str,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Permanently delete developer account (admin only).

    **Requirements:**
    - Must be an admin user
    - Valid admin access token in Authorization header

    **Warning:**
    - This action is irreversible
    - All associated data will be deleted
    - Properties and complexes will be orphaned

    **Use cases:**
    - Remove fraudulent accounts
    - Clean up test data
    - Compliance with data deletion requests
    """
    await developer_service.delete_developer(db, developer_id, admin_user)


# Developer properties management endpoints
@router.get(
    "/me/properties",
    response_model=dict,  # Will be a paginated property response
    summary="Get my properties",
    description="Get all properties for current developer with filtering and pagination",
)
async def get_my_properties(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status: Optional[str] = Query(None, description="Filter by property status"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    search: Optional[str] = Query(None, description="Search in property title or address"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get all properties for current developer with filtering and pagination.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **status**: Filter by property status (ACTIVE, SOLD, DRAFT, etc.)
    - **property_type**: Filter by property type (APARTMENT, HOUSE, etc.)
    - **city**: Filter by city name
    - **search**: Free text search in title or address

    **Returns:**
    - **items**: Array of property objects
    - **pagination**: Pagination metadata
    - **stats**: Summary statistics for all properties

    **Use cases:**
    - Developer property management dashboard
    - Property listing with filters
    - Property portfolio overview
    """
    # Get developer profile first
    developer_profile = await developer_service.get_developer_by_user_id(
        db, str(current_user.id)
    )

    if not developer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEVELOPER_PROFILE_NOT_FOUND",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await developer_service.get_developer_properties(
        db, str(developer_profile.id), page, limit, status, property_type, city, search
    )


@router.get(
    "/me/complexes",
    response_model=dict,  # Will be a paginated complex response
    summary="Get my complexes",
    description="Get all complexes for current developer with filtering and pagination",
)
async def get_my_complexes(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status: Optional[str] = Query(None, description="Filter by complex status"),
    city: Optional[str] = Query(None, description="Filter by city"),
    search: Optional[str] = Query(None, description="Search in complex name"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get all complexes for current developer with filtering and pagination.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **status**: Filter by complex status (ACTIVE, COMPLETED, UNDER_CONSTRUCTION, etc.)
    - **city**: Filter by city name
    - **search**: Free text search in complex name

    **Returns:**
    - **items**: Array of complex objects with property counts
    - **pagination**: Pagination metadata
    - **stats**: Summary statistics for all complexes

    **Use cases:**
    - Developer complex management dashboard
    - Complex listing with filters
    - Complex portfolio overview
    """
    # Get developer profile first
    developer_profile = await developer_service.get_developer_by_user_id(
        db, str(current_user.id)
    )

    if not developer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEVELOPER_PROFILE_NOT_FOUND",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await developer_service.get_developer_complexes(
        db, str(developer_profile.id), page, limit, status, city, search
    )


@router.post(
    "/me/verification-request",
    response_model=dict,
    summary="Submit verification request",
    description="Submit additional documents for developer verification",
)
async def submit_verification_request(
    documents: List[str] = Query(..., description="List of document URLs"),
    notes: Optional[str] = Query(None, description="Additional notes for verification"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Submit additional documents for developer verification.

    **Requirements:**
    - Must be logged in with DEVELOPER role
    - Valid access token in Authorization header
    - Developer must be in PENDING or REJECTED status

    **Request parameters:**
    - **documents**: List of document file URLs (uploaded separately)
    - **notes**: Optional additional notes for admin review

    **Document types that may be required:**
    - Company registration certificate
    - Tax registration documents
    - Bank account confirmation
    - Director's passport/ID
    - Power of attorney (if applicable)

    **Use cases:**
    - Initial verification submission
    - Re-submission after rejection
    - Additional document upload
    """
    # Get developer profile first
    developer_profile = await developer_service.get_developer_by_user_id(
        db, str(current_user.id)
    )

    if not developer_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "DEVELOPER_PROFILE_NOT_FOUND",
                    "message": "Профиль застройщика не найден",
                    "details": {},
                }
            },
        )

    return await developer_service.submit_verification_request(
        db, str(developer_profile.id), documents, notes
    )


# Public endpoints that don't require authentication
@router.get(
    "/public/search",
    response_model=DeveloperListPaginated,
    summary="Public developer search",
    description="Public search for verified developers (no auth required)",
)
async def public_search_developers(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=50, description="Number of items per page"),
    city: Optional[str] = Query(None, description="Filter by city"),
    rating_min: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    search: Optional[str] = Query(None, description="Search in company name"),
    db: AsyncSession = Depends(get_db),
) -> DeveloperListPaginated:
    """
    Public search for verified developers (no authentication required).

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 50)
    - **city**: Filter by city name
    - **rating_min**: Minimum rating threshold (0-5 scale)
    - **search**: Free text search in company names

    **Returns:**
    - Only verified developers (APPROVED status)
    - Basic information suitable for public display
    - Sorted by rating and activity

    **Use cases:**
    - Public developer directory
    - Property search results with developer info
    - Partner directory on website
    """
    params = DeveloperSearchParams(
        page=page,
        limit=limit,
        city=city,
        is_verified=True,  # Always filter to verified only
        rating_min=rating_min,
        search=search,
    )

    developers, total = await developer_service.get_public_developers_list(db, params)

    # Calculate pagination metadata
    pages = (total + limit - 1) // limit
    has_next = page < pages
    has_prev = page > 1
    
    pagination = PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev,
        next_page=page + 1 if has_next else None,
        prev_page=page - 1 if has_prev else None
    )
    
    return DeveloperListPaginated(
        items=developers,
        pagination=pagination
    )


@router.get(
    "/public/{developer_id}/properties",
    response_model=dict,
    summary="Get public developer properties",
    description="Get public properties for a specific developer (no auth required)",
)
async def get_public_developer_properties(
    developer_id: str,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=50, description="Number of items per page"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    price_min: Optional[int] = Query(None, ge=0, description="Minimum price filter"),
    price_max: Optional[int] = Query(None, ge=0, description="Maximum price filter"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get public properties for a specific developer (no authentication required).

    **Path parameters:**
    - **developer_id**: Developer UUID

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 50)
    - **property_type**: Filter by property type
    - **city**: Filter by city name
    - **price_min**: Minimum price filter
    - **price_max**: Maximum price filter

    **Returns:**
    - Only active properties from verified developers
    - Public property information
    - Developer basic information

    **Use cases:**
    - Developer profile page property listings
    - Property search by developer
    - Public developer portfolio display
    """
    return await developer_service.get_public_developer_properties(
        db, developer_id, page, limit, property_type, city, price_min, price_max
    )


@router.get(
    "/public/{developer_id}/complexes",
    response_model=dict,
    summary="Get public developer complexes",
    description="Get public complexes for a specific developer (no auth required)",
)
async def get_public_developer_complexes(
    developer_id: str,
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=50, description="Number of items per page"),
    city: Optional[str] = Query(None, description="Filter by city"),
    status: Optional[str] = Query(None, description="Filter by complex status"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get public complexes for a specific developer (no authentication required).

    **Path parameters:**
    - **developer_id**: Developer UUID

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 50)
    - **city**: Filter by city name
    - **status**: Filter by complex status

    **Returns:**
    - Only active complexes from verified developers
    - Public complex information with property counts
    - Developer basic information

    **Use cases:**
    - Developer profile page complex listings
    - Complex search by developer
    - Public developer portfolio display
    """
    return await developer_service.get_public_developer_complexes(
        db, developer_id, page, limit, city, status
    )
