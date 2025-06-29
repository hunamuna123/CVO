"""
Property API endpoints for property management and search.
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
from app.models.property import PropertyStatus
from app.schemas.property import (
    PropertyCreateRequest,
    PropertyListResponse,
    PropertyResponse,
    PropertySearchParams,
    PropertySearchResponse,
    PropertyStatusUpdateRequest,
    PropertyUpdateRequest,
)
from app.services.property_service import PropertyService
from app.utils.security import get_current_developer_user, get_current_user

router = APIRouter(prefix="/properties", tags=["Properties"])

# Initialize the property service
property_service = PropertyService()


@router.get(
    "/all",
    response_model=List[PropertyListResponse],
    summary="Get all properties",
    description="Get all active properties without pagination (for simple listings)",
    responses={
        200: {
            "description": "List of all active properties",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "3-комнатная квартира в ЖК 'Пресня Сити'",
                            "property_type": "APARTMENT",
                            "deal_type": "SALE",
                            "price": "15000000.00",
                            "price_per_sqm": "180000.00",
                            "currency": "RUB",
                            "city": "Москва",
                            "district": "Пресненский",
                            "total_area": 83.5,
                            "rooms_count": 3,
                            "floor": 15,
                            "total_floors": 25,
                            "has_parking": True,
                            "renovation_type": "EURO",
                            "status": "ACTIVE",
                            "is_featured": False,
                            "views_count": 245,
                            "favorites_count": 12,
                            "main_image_url": "https://example.com/image.jpg",
                            "developer_id": "550e8400-e29b-41d4-a716-446655440001",
                            "developer_name": "ПИК",
                            "developer_verified": True,
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-01-15T10:30:00Z"
                        }
                    ]
                }
            }
        }
    }
)
async def get_all_properties(
    db: AsyncSession = Depends(get_db),
) -> List[PropertyListResponse]:
    """
    Get all active properties without pagination.
    
    **Use cases:**
    - Property maps that need to show all locations
    - Export functionality for data analysis
    - Small UI components displaying property counts
    
    **Returns:**
    - All active properties with basic information
    - Sorted by creation date (newest first)
    - Only properties with ACTIVE status included
    
    **Performance note:**
    - This endpoint returns all properties at once
    - For large datasets, consider using the search endpoint with pagination
    - Response may be large, use with caution in production
    """
    return await property_service.get_all_properties(db)


@router.get(
    "/",
    response_model=PropertySearchResponse,
    summary="Search properties",
    description="Search properties with advanced filtering, sorting, and pagination",
    responses={
        200: {
            "description": "Successful property search with pagination",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "550e8400-e29b-41d4-a716-446655440000",
                                "title": "3-комнатная квартира в ЖК 'Пресня Сити'",
                                "property_type": "APARTMENT",
                                "deal_type": "SALE",
                                "price": "15000000.00",
                                "price_per_sqm": "180000.00",
                                "currency": "RUB",
                                "city": "Москва",
                                "district": "Пресненский",
                                "total_area": 83.5,
                                "rooms_count": 3,
                                "floor": 15,
                                "total_floors": 25,
                                "has_parking": True,
                                "renovation_type": "EURO",
                                "status": "ACTIVE",
                                "is_featured": False,
                                "views_count": 245,
                                "favorites_count": 12,
                                "main_image_url": "https://example.com/image.jpg",
                                "developer_id": "550e8400-e29b-41d4-a716-446655440001",
                                "developer_name": "ПИК",
                                "developer_verified": True,
                                "created_at": "2024-01-15T10:30:00Z",
                                "updated_at": "2024-01-15T10:30:00Z"
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
                        },
                        "search_time_ms": 45.2,
                        "filters_applied": {
                            "city": "Москва",
                            "rooms": "3",
                            "has_parking": True
                        },
                        "search_query": "Пресня"
                    }
                }
            }
        }
    }
)
async def search_properties(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(6, ge=1, le=100, description="Items per page"),
    property_type: Optional[str] = Query(
        None, description="Property type (APARTMENT, HOUSE, COMMERCIAL)"
    ),
    deal_type: Optional[str] = Query(None, description="Deal type (SALE, RENT)"),
    # New type filter with numeric mapping
    type: Optional[str] = Query(None, description="Property type: 0=дом, 1=квартира, 2=коммерческая"),
    region: Optional[str] = Query(None, description="Region filter"),
    city: Optional[str] = Query(None, description="City filter"),
    district: Optional[str] = Query(None, description="District filter"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
    total_area_min: Optional[float] = Query(
        None, gt=0, description="Minimum total area"
    ),
    total_area_max: Optional[float] = Query(
        None, gt=0, description="Maximum total area"
    ),
    rooms_count: Optional[str] = Query(
        None, description="Room counts (comma-separated: 1,2,3)"
    ),
    # New rooms filter with 4+ logic
    rooms: Optional[str] = Query(
        None, description="Rooms filter: single number or comma-separated (1,2,3,4). If 4+ specified, includes 4 and more"
    ),
    has_parking: Optional[bool] = Query(None, description="Has parking"),
    has_balcony: Optional[bool] = Query(None, description="Has balcony"),
    has_elevator: Optional[bool] = Query(None, description="Has elevator"),
    renovation_type: Optional[str] = Query(None, description="Renovation type"),
    # New peculiarity filter
    peculiarity: Optional[str] = Query(
        None, description="Comma-separated peculiarities: balcony,parking,playground,gym,ac,appliances,concierge,furniture"
    ),
    # New verify filter
    verify: Optional[str] = Query(
        None, description="Verification filters: verified,ai"
    ),
    building_year_min: Optional[int] = Query(
        None, ge=1800, description="Minimum building year"
    ),
    building_year_max: Optional[int] = Query(
        None, le=2100, description="Maximum building year"
    ),
    floor_min: Optional[int] = Query(None, ge=1, description="Minimum floor"),
    floor_max: Optional[int] = Query(None, ge=1, description="Maximum floor"),
    developer_id: Optional[str] = Query(None, description="Developer ID filter"),
    developer_verified: Optional[bool] = Query(
        None, description="Developer verification filter"
    ),
    is_featured: Optional[bool] = Query(None, description="Featured properties only"),
    # Enhanced sort options
    sort: Optional[str] = Query(
        "date_desc",
        description="Sort by: price_asc, price_desc, date_desc, date_asc, area_asc, area_desc, popular",
    ),
    search: Optional[str] = Query(None, description="Free text search in titles and other text fields"),
    lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Latitude for geographic search"
    ),
    lng: Optional[float] = Query(
        None, ge=-180, le=180, description="Longitude for geographic search"
    ),
    radius: Optional[int] = Query(None, ge=1, le=50, description="Search radius in km"),
    db: AsyncSession = Depends(get_db),
) -> PropertySearchResponse:
    """
    Search properties with advanced filtering and pagination.

    **Pagination parameters:**
    - **page**: Page number (default: 1, min: 1)
    - **limit**: Items per page (default: 20, min: 1, max: 100)

    **Basic filters:**
    - **property_type**: Property type (APARTMENT, HOUSE, COMMERCIAL)
    - **deal_type**: Deal type (SALE, RENT)
    - **type**: Numeric property type mapping (0=дом, 1=квартира, 2=коммерческая)

    **Location filters:**
    - **region**: Filter by region name (partial match)
    - **city**: Filter by city name (partial match)
    - **district**: Filter by district name (partial match)

    **Price filters:**
    - **price_min**: Minimum price in rubles (≥ 0)
    - **price_max**: Maximum price in rubles (≥ 0)

    **Area filters:**
    - **total_area_min**: Minimum total area in square meters (> 0)
    - **total_area_max**: Maximum total area in square meters (> 0)

    **Room filters:**
    - **rooms_count**: Legacy comma-separated room counts (e.g., "1,2,3")
    - **rooms**: Enhanced rooms filter with 4+ logic (e.g., "1,2,3,4")
      If "4" is specified, includes all properties with 4+ rooms

    **Feature filters:**
    - **has_parking**: Has parking space (true/false)
    - **has_balcony**: Has balcony or loggia (true/false)
    - **has_elevator**: Has elevator (true/false)
    - **renovation_type**: Renovation type (NONE, COSMETIC, EURO, DESIGNER)

    **Advanced feature filters:**
    - **peculiarity**: Comma-separated special features:
      - balcony: Balкон/лоджия
      - furniture: Мебель
      - parking: Парковка
      - gym: Фитнес-зал
      - ac: Кондиционер
      - appliances: Техника
      - concierge: Консьерж
      - playground: Детская площадка

    **Developer filters:**
    - **developer_id**: Filter by specific developer UUID
    - **developer_verified**: Show only verified developers (true/false)
    - **verify**: Verification filters (comma-separated):
      - verified: Верифицированные застройщики
      - ai: ИИ-оценка цены

    **Building filters:**
    - **building_year_min**: Minimum building year (≥ 1800)
    - **building_year_max**: Maximum building year (≤ 2100)
    - **floor_min**: Minimum floor number (≥ 1)
    - **floor_max**: Maximum floor number (≥ 1)

    **Status filters:**
    - **is_featured**: Show only featured properties (true/false)

    **Sorting options:**
    - **sort**: Sort order (default: date_desc)
      - price_asc: Сначала дешевые
      - price_desc: Сначала дорогие
      - date_desc (data_desc): Сначала новые
      - date_asc (data_asc): Сначала старые
      - area_asc: По площади (возрастание)
      - area_desc: По площади (убывание)
      - popular: По популярности (просмотры + избранное)

    **Search:**
    - **search**: Free text search in title, description, and address fields
      Supports partial matching and is case-insensitive

    **Geographic search:**
    - **lat**: Latitude for geographic search (-90 to 90)
    - **lng**: Longitude for geographic search (-180 to 180)
    - **radius**: Search radius in kilometers (1 to 50)
      All three parameters must be provided for geographic search

    **Response format:**
    Returns PropertySearchResponse with:
    - **items**: Array of property objects
    - **pagination**: Pagination metadata (page, total, has_next, etc.)
    - **search_time_ms**: Search execution time in milliseconds
    - **filters_applied**: Summary of applied filters
    - **search_query**: Search query used (if any)

    **Usage examples:**
    - `/properties?city=Москва&rooms=2,3&has_parking=true&sort=price_asc`
    - `/properties?type=1&peculiarity=balcony,parking&verify=verified`
    - `/properties?search=ЖК&price_min=5000000&price_max=15000000`
    - `/properties?lat=55.7558&lng=37.6176&radius=5`

    **Filter combinations:**
    All filters can be combined. The search uses AND logic between different
    filter types and OR logic within the same filter type (e.g., multiple rooms).
    """
    # Parse rooms_count
    rooms_list = None
    if rooms_count:
        try:
            rooms_list = [
                int(x.strip()) for x in rooms_count.split(",") if x.strip().isdigit()
            ]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_ROOMS_COUNT",
                        "message": "Некорректный формат количества комнат",
                        "details": {"rooms_count": rooms_count},
                    }
                },
            )

    search_params = PropertySearchParams(
        page=page,
        limit=limit,
        property_type=property_type,
        deal_type=deal_type,
        type=type,  # New numeric type filter
        region=region,
        city=city,
        district=district,
        price_min=price_min,
        price_max=price_max,
        total_area_min=total_area_min,
        total_area_max=total_area_max,
        rooms_count=rooms_list,
        rooms=rooms,  # New rooms filter with 4+ logic
        has_parking=has_parking,
        has_balcony=has_balcony,
        has_elevator=has_elevator,
        renovation_type=renovation_type,
        peculiarity=peculiarity,  # New peculiarity filter
        verify=verify,  # New verify filter
        building_year_min=building_year_min,
        building_year_max=building_year_max,
        floor_min=floor_min,
        floor_max=floor_max,
        developer_id=developer_id,
        developer_verified=developer_verified,
        is_featured=is_featured,
        sort=sort,
        search=search,
        lat=lat,
        lng=lng,
        radius=radius,
    )

    return await property_service.search_properties(db, search_params)


@router.get(
    "/featured",
    response_model=List[PropertyListResponse],
    summary="Get featured properties",
    description="Get a list of featured properties for homepage or promotional sections",
)
async def get_featured_properties(
    limit: int = Query(10, ge=1, le=50, description="Number of properties to return"),
    db: AsyncSession = Depends(get_db),
) -> List[PropertyListResponse]:
    """
    Get featured properties.

    Returns a list of featured properties sorted by creation date.
    Perfect for homepage sections or promotional displays.
    """
    return await property_service.get_featured_properties(db, limit)


@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Get property details",
    description="Get detailed information about a specific property",
)
async def get_property(
    property_id: str,
    increment_views: bool = Query(True, description="Whether to increment view count"),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    """
    Get detailed property information by ID.

    **Path parameters:**
    - **property_id**: Property UUID

    **Query parameters:**
    - **increment_views**: Whether to increment view counter (default: true)

    Returns complete property information including:
    - All property details and characteristics
    - Images and documents
    - Developer information
    - Location and contact details
    """
    return await property_service.get_property_by_id(db, property_id, increment_views)


@router.post(
    "",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new property",
    description="Create a new property listing (developer only)",
)
async def create_property(
    property_data: PropertyCreateRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    """
    Create a new property listing.

    **Requirements:**
    - Must be a verified developer
    - Valid access token in Authorization header

    **Request body:**
    All property details including title, description, location,
    characteristics, and features.

    **Property lifecycle:**
    - Created with DRAFT status
    - Can be updated and published later
    - Requires images and documents for activation
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

    return await property_service.create_property(
        db, property_data, str(current_user.developer_profile.id)
    )


@router.put(
    "/{property_id}",
    response_model=PropertyResponse,
    summary="Update property",
    description="Update property information (owner only)",
)
async def update_property(
    property_id: str,
    property_data: PropertyUpdateRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    """
    Update property information.

    **Requirements:**
    - Must be the property owner (developer)
    - Valid access token in Authorization header

    **Updatable fields:**
    - Basic information (title, description, price)
    - Location details
    - Property characteristics
    - Features and amenities
    - Availability dates

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

    return await property_service.update_property(
        db, property_id, property_data, str(current_user.developer_profile.id)
    )


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete property",
    description="Delete property listing (owner only)",
)
async def delete_property(
    property_id: str,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete property listing.

    **Requirements:**
    - Must be the property owner (developer)
    - Valid access token in Authorization header

    **Warning:** This action cannot be undone.
    All associated images, documents, and data will be permanently deleted.
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

    await property_service.delete_property(
        db, property_id, str(current_user.developer_profile.id)
    )

    return {"message": "Property deleted successfully"}


@router.put(
    "/{property_id}/status",
    response_model=PropertyResponse,
    summary="Update property status",
    description="Update property status (owner only)",
)
async def update_property_status(
    property_id: str,
    status_data: PropertyStatusUpdateRequest,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    """
    Update property status.

    **Requirements:**
    - Must be the property owner (developer)
    - Valid access token in Authorization header

    **Available statuses:**
    - **DRAFT**: Property is being prepared
    - **ACTIVE**: Property is published and visible
    - **SOLD**: Property has been sold
    - **RENTED**: Property has been rented
    - **ARCHIVED**: Property is no longer available

    **Status transitions:**
    - DRAFT → ACTIVE (publish property)
    - ACTIVE → SOLD/RENTED (mark as unavailable)
    - Any status → ARCHIVED (remove from listings)
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

    return await property_service.update_property_status(
        db, property_id, status_data.status, str(current_user.developer_profile.id)
    )


@router.post(
    "/{property_id}/images",
    response_model=List[dict],
    summary="Upload property images",
    description="Upload images for a property (owner only)",
)
async def upload_property_images(
    property_id: str,
    files: List[UploadFile] = File(..., description="Image files to upload"),
    titles: Optional[str] = Form(None, description="Comma-separated image titles"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Upload images for a property.

    **Requirements:**
    - Must be the property owner (developer)
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

    return await property_service.upload_property_images(
        db, property_id, files, str(current_user.developer_profile.id), titles_list
    )


@router.post(
    "/{property_id}/documents",
    response_model=List[dict],
    summary="Upload property documents",
    description="Upload documents for a property (owner only)",
)
async def upload_property_documents(
    property_id: str,
    files: List[UploadFile] = File(..., description="Document files to upload"),
    titles: str = Form(..., description="Comma-separated document titles"),
    document_types: str = Form(..., description="Comma-separated document types"),
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
) -> List[dict]:
    """
    Upload documents for a property.

    **Requirements:**
    - Must be the property owner (developer)
    - Valid access token in Authorization header

    **File requirements:**
    - Supported formats: PDF, DOC, DOCX, TXT
    - Maximum file size: 50MB per document
    - Files are stored securely with access control

    **Document types:**
    - **PLAN**: Floor plans and layouts
    - **CERTIFICATE**: Certificates and permits
    - **CONTRACT**: Contract templates
    - **OTHER**: Other documents

    **Form data:**
    - **files**: Multiple document files
    - **titles**: Comma-separated list of document titles (required)
    - **document_types**: Comma-separated list of document types (required)

    **Note:** Number of titles and types must match number of files.
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

    # Parse titles and types
    titles_list = [title.strip() for title in titles.split(",")]
    types_list = [doc_type.strip() for doc_type in document_types.split(",")]

    # Validate counts
    if len(titles_list) != len(files) or len(types_list) != len(files):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "MISMATCHED_METADATA",
                    "message": "Количество названий и типов должно соответствовать количеству файлов",
                    "details": {
                        "files_count": len(files),
                        "titles_count": len(titles_list),
                        "types_count": len(types_list),
                    },
                }
            },
        )

    return await property_service.upload_property_documents(
        db,
        property_id,
        files,
        str(current_user.developer_profile.id),
        titles_list,
        types_list,
    )


@router.delete(
    "/{property_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete property image",
    description="Delete a specific property image (owner only)",
)
async def delete_property_image(
    property_id: str,
    image_id: str,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific property image.

    **Requirements:**
    - Must be the property owner (developer)
    - Valid access token in Authorization header

    **Warning:** This action cannot be undone.
    The image file will be permanently deleted from storage.
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

    await property_service.delete_property_image(
        db, property_id, image_id, str(current_user.developer_profile.id)
    )


@router.delete(
    "/{property_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete property document",
    description="Delete a specific property document (owner only)",
)
async def delete_property_document(
    property_id: str,
    document_id: str,
    current_user: User = Depends(get_current_developer_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific property document.

    **Requirements:**
    - Must be the property owner (developer)
    - Valid access token in Authorization header

    **Warning:** This action cannot be undone.
    The document file will be permanently deleted from storage.
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

    await property_service.delete_property_document(
        db, property_id, document_id, str(current_user.developer_profile.id)
    )
