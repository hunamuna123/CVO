"""
Developer API endpoints for registration, management, and verification.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.auth import AuthResponse
from app.schemas.developer import (
    DeveloperListResponse,
    DeveloperRegisterRequest,
    DeveloperResponse,
    DeveloperSearchParams,
    DeveloperUpdateRequest,
    DeveloperVerificationRequest,
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
    "",
    response_model=List[DeveloperListResponse],
    summary="Get developers list",
    description="Get paginated list of developers with filtering and search",
)
async def get_developers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    city: str = Query(None, description="Filter by city"),
    is_verified: bool = Query(None, description="Filter by verification status"),
    rating_min: float = Query(None, ge=0, le=5, description="Minimum rating"),
    search: str = Query(None, description="Search in company name"),
    db: AsyncSession = Depends(get_db),
) -> List[DeveloperListResponse]:
    """
    Get list of developers with filtering and pagination.

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **city**: Filter by city
    - **is_verified**: Filter by verification status (true/false)
    - **rating_min**: Minimum rating (0-5)
    - **search**: Search in company name

    Returns list of developers with basic information and statistics.
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

    # Add pagination headers (could be moved to middleware)
    # For now, returning just the list
    return developers


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
