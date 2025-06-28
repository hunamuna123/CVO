"""
Property schemas for request and response models.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.property import DealType, PropertyStatus, PropertyType, RenovationType


# Base schemas
class PropertyImageBase(BaseModel):
    """Base property image schema."""

    url: str
    title: Optional[str] = None
    is_main: bool = False
    order: int = 0


class PropertyImageResponse(PropertyImageBase):
    """Property image response schema."""

    id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PropertyDocumentBase(BaseModel):
    """Base property document schema."""

    title: str
    document_type: str
    file_url: str
    file_size: int
    mime_type: str


class PropertyDocumentResponse(PropertyDocumentBase):
    """Property document response schema."""

    id: str
    is_verified: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# Property create/update schemas
class PropertyCreateRequest(BaseModel):
    """Property creation request schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    property_type: PropertyType
    deal_type: DealType
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="RUB", max_length=3)

    # Address
    region: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., min_length=1, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    street: str = Field(..., min_length=1, max_length=255)
    house_number: str = Field(..., min_length=1, max_length=50)
    apartment_number: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Characteristics
    total_area: Optional[float] = Field(None, gt=0)
    living_area: Optional[float] = Field(None, gt=0)
    kitchen_area: Optional[float] = Field(None, gt=0)
    rooms_count: Optional[int] = Field(None, ge=0)
    bedrooms_count: Optional[int] = Field(None, ge=0)
    bathrooms_count: Optional[int] = Field(None, ge=0)
    floor: Optional[int] = Field(None, ge=0)
    total_floors: Optional[int] = Field(None, ge=1)
    building_year: Optional[int] = Field(None, ge=1800, le=2100)
    ceiling_height: Optional[float] = Field(None, gt=0, le=10)

    # Features
    has_balcony: bool = False
    has_loggia: bool = False
    has_elevator: bool = False
    has_parking: bool = False
    has_furniture: bool = False
    renovation_type: Optional[RenovationType] = None

    # Availability
    available_from: Optional[date] = None

    @field_validator("living_area")
    @classmethod
    def validate_living_area(cls, v, info):
        """Validate living area is not greater than total area."""
        if v is not None and info.data.get("total_area") is not None:
            if v > info.data["total_area"]:
                raise ValueError("Living area cannot be greater than total area")
        return v

    @field_validator("kitchen_area")
    @classmethod
    def validate_kitchen_area(cls, v, info):
        """Validate kitchen area is reasonable."""
        if v is not None and info.data.get("total_area") is not None:
            if v > info.data["total_area"]:
                raise ValueError("Kitchen area cannot be greater than total area")
        return v

    @field_validator("floor")
    @classmethod
    def validate_floor(cls, v, info):
        """Validate floor is not greater than total floors."""
        if v is not None and info.data.get("total_floors") is not None:
            if v > info.data["total_floors"]:
                raise ValueError("Floor cannot be greater than total floors")
        return v


class PropertyUpdateRequest(BaseModel):
    """Property update request schema."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[Decimal] = Field(None, gt=0)

    # Address
    region: Optional[str] = Field(None, min_length=1, max_length=100)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    street: Optional[str] = Field(None, min_length=1, max_length=255)
    house_number: Optional[str] = Field(None, min_length=1, max_length=50)
    apartment_number: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Characteristics
    total_area: Optional[float] = Field(None, gt=0)
    living_area: Optional[float] = Field(None, gt=0)
    kitchen_area: Optional[float] = Field(None, gt=0)
    rooms_count: Optional[int] = Field(None, ge=0)
    bedrooms_count: Optional[int] = Field(None, ge=0)
    bathrooms_count: Optional[int] = Field(None, ge=0)
    floor: Optional[int] = Field(None, ge=0)
    total_floors: Optional[int] = Field(None, ge=1)
    building_year: Optional[int] = Field(None, ge=1800, le=2100)
    ceiling_height: Optional[float] = Field(None, gt=0, le=10)

    # Features
    has_balcony: Optional[bool] = None
    has_loggia: Optional[bool] = None
    has_elevator: Optional[bool] = None
    has_parking: Optional[bool] = None
    has_furniture: Optional[bool] = None
    renovation_type: Optional[RenovationType] = None

    # Availability
    available_from: Optional[date] = None


class PropertyStatusUpdateRequest(BaseModel):
    """Property status update request schema."""

    status: PropertyStatus


# Property response schemas
class PropertyListResponse(BaseModel):
    """Property list item response schema."""

    id: str
    title: str
    property_type: PropertyType
    deal_type: DealType
    price: Decimal
    price_per_sqm: Optional[Decimal] = None
    currency: str

    # Location
    city: str
    district: Optional[str] = None

    # Basic characteristics
    total_area: Optional[float] = None
    rooms_count: Optional[int] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None

    # Features
    has_parking: bool
    renovation_type: Optional[RenovationType] = None

    # Status
    status: PropertyStatus
    is_featured: bool

    # Metrics
    views_count: int
    favorites_count: int

    # Main image
    main_image_url: Optional[str] = None

    # Developer info
    developer_id: str
    developer_name: str
    developer_verified: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PropertyResponse(BaseModel):
    """Detailed property response schema."""

    id: str
    title: str
    description: str
    property_type: PropertyType
    deal_type: DealType
    price: Decimal
    price_per_sqm: Optional[Decimal] = None
    currency: str

    # Address
    region: str
    city: str
    district: Optional[str] = None
    street: str
    house_number: str
    apartment_number: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    full_address: str

    # Characteristics
    total_area: Optional[float] = None
    living_area: Optional[float] = None
    kitchen_area: Optional[float] = None
    rooms_count: Optional[int] = None
    bedrooms_count: Optional[int] = None
    bathrooms_count: Optional[int] = None
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    building_year: Optional[int] = None
    ceiling_height: Optional[float] = None

    # Features
    has_balcony: bool
    has_loggia: bool
    has_elevator: bool
    has_parking: bool
    has_furniture: bool
    renovation_type: Optional[RenovationType] = None

    # Status
    status: PropertyStatus
    is_featured: bool

    # Metrics
    views_count: int
    favorites_count: int

    # Availability
    available_from: Optional[date] = None

    # Media
    images: List[PropertyImageResponse] = []
    documents: List[PropertyDocumentResponse] = []

    # Developer info
    developer_id: str
    developer: dict  # Basic developer info

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Search and filter schemas
class PropertySearchParams(BaseModel):
    """Property search parameters schema."""

    # Pagination
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    # Basic filters
    property_type: Optional[PropertyType] = None
    deal_type: Optional[DealType] = None

    # Location filters
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None

    # Price filters
    price_min: Optional[Decimal] = Field(None, ge=0)
    price_max: Optional[Decimal] = Field(None, ge=0)

    # Area filters
    total_area_min: Optional[float] = Field(None, gt=0)
    total_area_max: Optional[float] = Field(None, gt=0)

    # Room filters
    rooms_count: Optional[List[int]] = Field(None, description="List of room counts")

    # Feature filters
    has_parking: Optional[bool] = None
    has_balcony: Optional[bool] = None
    has_elevator: Optional[bool] = None
    renovation_type: Optional[RenovationType] = None

    # Building filters
    building_year_min: Optional[int] = Field(None, ge=1800)
    building_year_max: Optional[int] = Field(None, le=2100)
    floor_min: Optional[int] = Field(None, ge=1)
    floor_max: Optional[int] = Field(None, ge=1)

    # Developer filter
    developer_id: Optional[str] = None
    developer_verified: Optional[bool] = None

    # Status filters
    status: Optional[List[PropertyStatus]] = None
    is_featured: Optional[bool] = None

    # Sorting
    sort: Optional[str] = Field(
        default="created_desc",
        description="Sort by: price_asc, price_desc, created_desc, area_asc, area_desc, popular",
    )

    # Search query
    search: Optional[str] = Field(None, description="Free text search")

    # Geographic search
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    radius: Optional[int] = Field(None, ge=1, le=50, description="Search radius in km")

    @field_validator("price_max")
    @classmethod
    def validate_price_range(cls, v, info):
        """Validate price range."""
        if v is not None and info.data.get("price_min") is not None:
            if v < info.data["price_min"]:
                raise ValueError("price_max must be greater than price_min")
        return v

    @field_validator("total_area_max")
    @classmethod
    def validate_area_range(cls, v, info):
        """Validate area range."""
        if v is not None and info.data.get("total_area_min") is not None:
            if v < info.data["total_area_min"]:
                raise ValueError("total_area_max must be greater than total_area_min")
        return v


class PropertySearchResponse(BaseModel):
    """Property search response schema."""

    items: List[PropertyListResponse]
    total: int
    page: int
    limit: int
    pages: int

    # Search metadata
    search_time_ms: Optional[float] = None
    filters_applied: dict = {}


# File upload schemas
class PropertyImageUploadResponse(BaseModel):
    """Property image upload response schema."""

    id: str
    url: str
    thumbnail_url: Optional[str] = None
    title: Optional[str] = None
    is_main: bool
    order: int


class PropertyDocumentUploadResponse(BaseModel):
    """Property document upload response schema."""

    id: str
    title: str
    document_type: str
    file_url: str
    file_size: int
    mime_type: str
