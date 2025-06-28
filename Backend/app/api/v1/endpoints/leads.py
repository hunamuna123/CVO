"""
Leads API endpoints for managing property inquiries and contacts.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.lead import (
    LeadCreateRequest,
    LeadListResponse,
    LeadResponse,
    LeadSearchParams,
    LeadStatusUpdateRequest,
)
from app.services.lead_service import LeadService
from app.utils.security import get_current_developer_user, get_current_user_optional

router = APIRouter(prefix="/leads", tags=["Leads"])

# Initialize the lead service
lead_service = LeadService()


@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lead",
    description="Create a new lead inquiry for a property",
)
async def create_lead(
    lead_data: LeadCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> LeadResponse:
    """
    Create a new lead inquiry.

    **Request body:**
    - **property_id**: UUID of the property (required)
    - **name**: Contact person name (required)
    - **phone**: Contact phone number (required)
    - **email**: Contact email (optional)
    - **message**: Additional message (optional)
    - **lead_type**: Type of inquiry (CALL_REQUEST, VIEWING, CONSULTATION)

    **Notes:**
    - Anonymous users can create leads
    - If user is authenticated, user_id will be automatically set
    - Lead will be forwarded to the property developer
    """
    user_id = str(current_user.id) if current_user else None
    return await lead_service.create_lead(db, lead_data, user_id)


@router.get(
    "",
    response_model=List[LeadListResponse],
    summary="Get developer leads",
    description="Get leads for developer properties with filtering",
)
async def get_developer_leads(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    property_id: Optional[str] = Query(None, description="Filter by property ID"),
    lead_type: Optional[str] = Query(
        None, description="Filter by lead type (CALL_REQUEST, VIEWING, CONSULTATION)"
    ),
    status: Optional[str] = Query(
        None, description="Filter by status (NEW, IN_PROGRESS, COMPLETED, CANCELLED)"
    ),
    date_from: Optional[str] = Query(
        None, description="Filter from date (YYYY-MM-DD)"
    ),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    sort: Optional[str] = Query(
        "created_desc",
        description="Sort by: created_desc, created_asc, status_asc, priority_desc",
    ),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> List[LeadListResponse]:
    """
    Get leads for developer properties.

    **Requirements:**
    - Valid access token in Authorization header
    - Must be a verified developer

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **property_id**: Filter by specific property
    - **lead_type**: Filter by lead type
    - **status**: Filter by lead status
    - **date_from**: Filter from date (YYYY-MM-DD)
    - **date_to**: Filter to date (YYYY-MM-DD)
    - **sort**: Sorting option

    Returns paginated list of leads for developer's properties.
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

    search_params = LeadSearchParams(
        page=page,
        limit=limit,
        property_id=property_id,
        lead_type=lead_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
        sort=sort,
    )

    return await lead_service.get_developer_leads(
        db, str(current_user.developer_profile.id), search_params
    )


@router.get(
    "/stats",
    response_model=dict,
    summary="Get lead statistics",
    description="Get lead statistics for developer",
)
async def get_lead_stats(
    period: Optional[str] = Query(
        "month", description="Statistics period (week, month, quarter, year)"
    ),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get lead statistics for developer.

    **Requirements:**
    - Valid access token in Authorization header
    - Must be a verified developer

    **Query parameters:**
    - **period**: Statistics period (week, month, quarter, year)

    Returns statistics including:
    - Total leads count
    - Leads by status
    - Leads by type
    - Conversion rates
    - Trends over time
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

    return await lead_service.get_lead_stats(
        db, str(current_user.developer_profile.id), period
    )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Get lead details",
    description="Get detailed information about a specific lead",
)
async def get_lead(
    lead_id: str,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Get detailed lead information by ID.

    **Requirements:**
    - Valid access token in Authorization header
    - Must be a verified developer
    - Lead must belong to developer's property

    **Path parameters:**
    - **lead_id**: Lead UUID

    Returns complete lead information including contact details and history.
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

    return await lead_service.get_lead_by_id(
        db, lead_id, str(current_user.developer_profile.id)
    )


@router.put(
    "/{lead_id}/status",
    response_model=LeadResponse,
    summary="Update lead status",
    description="Update lead status and add notes",
)
async def update_lead_status(
    lead_id: str,
    status_data: LeadStatusUpdateRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Update lead status.

    **Requirements:**
    - Valid access token in Authorization header
    - Must be a verified developer
    - Lead must belong to developer's property

    **Request body:**
    - **status**: New status (NEW, IN_PROGRESS, COMPLETED, CANCELLED)
    - **notes**: Optional notes about status change

    **Available status transitions:**
    - NEW → IN_PROGRESS (start working on lead)
    - IN_PROGRESS → COMPLETED (lead converted successfully)
    - IN_PROGRESS → CANCELLED (lead cancelled or failed)
    - Any status → IN_PROGRESS (reopen lead)
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

    return await lead_service.update_lead_status(
        db, lead_id, status_data, str(current_user.developer_profile.id)
    )


@router.get(
    "/my/inquiries",
    response_model=List[LeadListResponse],
    summary="Get user's inquiries",
    description="Get all inquiries created by the current user",
)
async def get_my_inquiries(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> List[LeadListResponse]:
    """
    Get all inquiries created by the current user.

    **Requirements:**
    - Valid access token in Authorization header

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)

    Returns paginated list of user's inquiries with status information.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Необходима аутентификация",
                    "details": {},
                }
            },
        )

    return await lead_service.get_user_inquiries(
        db, str(current_user.id), page, limit
    )
