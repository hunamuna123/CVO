"""
Complex API endpoints for residential complex management.
"""

from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Developer, User
from app.schemas.complex import (
    ComplexCreateRequest,
    ComplexListResponse,
    ComplexResponse,
    ComplexSearchParams,
    ComplexSearchResponse,
    ComplexUpdateRequest,
)
from app.services.complex_service import ComplexService
from app.utils.security import get_current_developer_user, get_current_user

router = APIRouter(prefix="/complexes", tags=["Complexes"])

# Initialize the complex service
complex_service = ComplexService()


@router.get(
    "/",
    response_model=ComplexSearchResponse,
    summary="Search complexes",
    description="Search residential complexes with advanced filtering and pagination",
)
async def search_complexes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    complex_class: Optional[str] = Query(
        None, description="Complex class (ECONOMY, COMFORT, BUSINESS, ELITE, PREMIUM)"
    ),
    status: Optional[str] = Query(
        None, description="Complex status (PLANNED, CONSTRUCTION, READY, DELIVERED)"
    ),
    region: Optional[str] = Query(None, description="Region filter"),
    city: Optional[str] = Query(None, description="City filter"),
    district: Optional[str] = Query(None, description="District filter"),
    price_from: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_to: Optional[float] = Query(None, ge=0, description="Maximum price"),
    developer_id: Optional[str] = Query(None, description="Developer ID filter"),
    developer_verified: Optional[bool] = Query(
        None, description="Developer verification filter"
    ),
    is_featured: Optional[bool] = Query(None, description="Featured complexes only"),
    has_parking: Optional[bool] = Query(None, description="Has parking"),
    has_playground: Optional[bool] = Query(None, description="Has playground"),
    has_school: Optional[bool] = Query(None, description="Has school nearby"),
    has_kindergarten: Optional[bool] = Query(None, description="Has kindergarten nearby"),
    has_shopping_center: Optional[bool] = Query(None, description="Has shopping center nearby"),
    has_fitness_center: Optional[bool] = Query(None, description="Has fitness center"),
    construction_year_from: Optional[int] = Query(
        None, ge=2000, description="Construction start year from"
    ),
    construction_year_to: Optional[int] = Query(
        None, le=2030, description="Construction start year to"
    ),
    completion_year_from: Optional[int] = Query(
        None, ge=2020, description="Completion year from"
    ),
    completion_year_to: Optional[int] = Query(
        None, le=2035, description="Completion year to"
    ),
    sort: Optional[str] = Query(
        "created_desc",
        description="Sort by: price_asc, price_desc, created_desc, name_asc, completion_asc",
    ),
    search: Optional[str] = Query(None, description="Free text search"),
    lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Latitude for geographic search"
    ),
    lng: Optional[float] = Query(
        None, ge=-180, le=180, description="Longitude for geographic search"
    ),
    radius: Optional[int] = Query(None, ge=1, le=50, description="Search radius in km"),
    db: AsyncSession = Depends(get_db),
) -> ComplexSearchResponse:
    """
    Search residential complexes with advanced filtering and pagination.

    **Query parameters:**
    - **page**: Page number (default: 1)
    - **limit**: Items per page (default: 20, max: 100)
    - **complex_class**: ECONOMY, COMFORT, BUSINESS, ELITE, PREMIUM
    - **status**: PLANNED, CONSTRUCTION, READY, DELIVERED
    - **region, city, district**: Location filters
    - **price_from, price_to**: Price range filters
    - **developer_id**: Filter by specific developer
    - **developer_verified**: Filter by developer verification status
    - **is_featured**: Show only featured complexes
    - **has_parking, has_playground, etc.**: Infrastructure filters
    - **construction_year_from/to**: Construction year range
    - **completion_year_from/to**: Completion year range
    - **sort**: Sorting option
    - **search**: Free text search in name, description, address
    - **lat, lng, radius**: Geographic search

    Returns paginated search results with metadata.
    """
    search_params = ComplexSearchParams(
        page=page,
        limit=limit,
        complex_class=complex_class,
        status=status,
        region=region,
        city=city,
        district=district,
        price_from=price_from,
        price_to=price_to,
        developer_id=developer_id,
        developer_verified=developer_verified,
        is_featured=is_featured,
        has_parking=has_parking,
        has_playground=has_playground,
        has_school=has_school,
        has_kindergarten=has_kindergarten,
        has_shopping_center=has_shopping_center,
        has_fitness_center=has_fitness_center,
        construction_year_from=construction_year_from,
        construction_year_to=construction_year_to,
        completion_year_from=completion_year_from,
        completion_year_to=completion_year_to,
        sort=sort,
        search=search,
        lat=lat,
        lng=lng,
        radius=radius,
    )

    return await complex_service.search_complexes(db, search_params)


@router.get(
    "/featured",
    response_model=List[ComplexListResponse],
    summary="Get featured complexes",
    description="Get a list of featured complexes for homepage or promotional sections",
)
async def get_featured_complexes(
    limit: int = Query(10, ge=1, le=50, description="Number of complexes to return"),
    db: AsyncSession = Depends(get_db),
) -> List[ComplexListResponse]:
    """
    Get featured complexes.

    Returns a list of featured complexes sorted by creation date.
    Perfect for homepage sections or promotional displays.
    """
    return await complex_service.get_featured_complexes(db, limit)


@router.get(
    "/{complex_id}",
    response_model=ComplexResponse,
    summary="Get complex details",
    description="Get detailed information about a specific complex",
)
async def get_complex(
    complex_id: str,
    db: AsyncSession = Depends(get_db),
) -> ComplexResponse:
    """
    Get detailed complex information by ID.

    **Path parameters:**
    - **complex_id**: Complex UUID

    Returns complete complex information including:
    - All complex details and characteristics
    - Images and infrastructure
    - Developer information
    - Location and contact details
    - Properties count and statistics
    """
    return await complex_service.get_complex_by_id(db, complex_id)


@router.post(
    "",
    response_model=ComplexResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new complex",
    description="Create a new residential complex (developer only)",
)
async def create_complex(
    complex_data: ComplexCreateRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> ComplexResponse:
    """
    Create a new residential complex.

    **Requirements:**
    - Must be a verified developer
    - Valid access token in Authorization header

    **Request body:**
    All complex details including name, description, location,
    status, class, and infrastructure features.

    **Complex lifecycle:**
    - Created with specified status
    - Can be updated and managed later
    - Requires images for better visibility
    """
    # Get developer profile
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

    return await complex_service.create_complex(
        db, complex_data, str(current_user.developer_profile.id)
    )


@router.put(
    "/{complex_id}",
    response_model=ComplexResponse,
    summary="Update complex",
    description="Update complex information (owner only)",
)
async def update_complex(
    complex_id: str,
    complex_data: ComplexUpdateRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> ComplexResponse:
    """
    Update complex information.

    **Requirements:**
    - Must be the complex owner (developer)
    - Valid access token in Authorization header

    **Updatable fields:**
    - Basic information (name, description)
    - Location details
    - Complex characteristics and infrastructure
    - Dates and completion status
    - Media URLs

    **Note:** Some fields may require admin approval for changes.
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

    return await complex_service.update_complex(
        db, complex_id, complex_data, str(current_user.developer_profile.id)
    )


@router.delete(
    "/{complex_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete complex",
    description="Delete complex (owner only)",
)
async def delete_complex(
    complex_id: str,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete complex.

    **Requirements:**
    - Must be the complex owner (developer)
    - Valid access token in Authorization header

    **Warning:** This action cannot be undone.
    All associated properties, images, and data will be permanently deleted.
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

    await complex_service.delete_complex(
        db, complex_id, str(current_user.developer_profile.id)
    )

    return {"message": "Complex deleted successfully"}


@router.post(
    "/{complex_id}/images",
    response_model=List[dict],
    summary="Upload complex images",
    description="Upload images for a complex (owner only)",
)
async def upload_complex_images(
    complex_id: str,
    files: List[UploadFile] = File(..., description="Image files to upload"),
    titles: Optional[str] = Form(None, description="Comma-separated image titles"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Upload images for a complex.

    **Requirements:**
    - Must be the complex owner (developer)
    - Valid access token in Authorization header

    **File requirements:**
    - Supported formats: JPG, JPEG, PNG, WebP
    - Maximum file size: 50MB per image
    - Images will be automatically optimized and converted to WebP
    - Thumbnails will be generated automatically

    **Features:**
    - First uploaded image becomes the main image
    - Images are stored with proper organization
    - Automatic image optimization and compression
    - Generate multiple sizes for different use cases

    **Form data:**
    - **files**: Multiple image files
    - **titles**: Optional comma-separated list of image titles
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

    # Parse titles
    titles_list = None
    if titles:
        titles_list = [title.strip() for title in titles.split(",")]

    return await complex_service.upload_complex_images(
        db, complex_id, files, str(current_user.developer_profile.id), titles_list
    )


@router.get(
    "/{complex_id}/properties",
    response_model=List[dict],
    summary="Get complex properties",
    description="Get all properties in a complex",
)
async def get_complex_properties(
    complex_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    status: Optional[str] = Query(None, description="Filter by property status"),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Get all properties in a complex.

    **Path parameters:**
    - **complex_id**: Complex UUID

    **Query parameters:**
    - **page**: Page number
    - **limit**: Items per page
    - **property_type**: Filter by property type
    - **status**: Filter by property status

    Returns list of properties with basic information.
    """
    return await complex_service.get_complex_properties(
        db, complex_id, page, limit, property_type, status
    )


@router.get(
    "/{complex_id}/analytics",
    response_model=dict,
    summary="Get complex analytics",
    description="Get analytics for a complex (owner only)",
)
async def get_complex_analytics(
    complex_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get analytics for a complex.

    **Requirements:**
    - Must be the complex owner (developer)
    - Valid access token in Authorization header

    **Analytics include:**
    - Properties count and status distribution
    - Views and interest metrics
    - Sales performance
    - Price trends
    - Popular property types
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

    return await complex_service.get_complex_analytics(
        db, complex_id, str(current_user.developer_profile.id), days
    )
