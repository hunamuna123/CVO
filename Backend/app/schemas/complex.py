"""
Complex schemas for API requests and responses.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.complex import ComplexClass, ComplexStatus


# Base schemas
class ComplexBase(BaseModel):
    """Base complex schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Complex name")
    description: str = Field(..., min_length=10, description="Complex description")
    complex_class: ComplexClass = Field(..., description="Complex class")
    
    # Location
    region: str = Field(..., min_length=1, max_length=100, description="Region")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    district: Optional[str] = Field(None, max_length=100, description="District")
    address: str = Field(..., min_length=5, max_length=500, description="Full address")
    
    # Coordinates
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")


class ComplexCreateRequest(ComplexBase):
    """Schema for creating a new complex."""
    
    # Construction information
    status: ComplexStatus = Field(default=ComplexStatus.PLANNED, description="Complex status")
    construction_start_date: Optional[date] = Field(None, description="Construction start date")
    planned_completion_date: Optional[date] = Field(None, description="Planned completion date")
    actual_completion_date: Optional[date] = Field(None, description="Actual completion date")
    
    # Buildings information
    total_buildings: Optional[int] = Field(None, ge=1, description="Total number of buildings")
    total_apartments: Optional[int] = Field(None, ge=1, description="Total number of apartments")
    
    # Price information
    price_from: Optional[Decimal] = Field(None, ge=0, description="Starting price")
    price_to: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    
    # Infrastructure
    has_parking: bool = Field(default=False, description="Has parking")
    has_playground: bool = Field(default=False, description="Has playground")
    has_school: bool = Field(default=False, description="Has school nearby")
    has_kindergarten: bool = Field(default=False, description="Has kindergarten nearby")
    has_shopping_center: bool = Field(default=False, description="Has shopping center nearby")
    has_fitness_center: bool = Field(default=False, description="Has fitness center")
    has_concierge: bool = Field(default=False, description="Has concierge service")
    has_security: bool = Field(default=False, description="Has security")
    
    # Features
    is_featured: bool = Field(default=False, description="Featured complex")
    
    # Media
    main_image_url: Optional[str] = Field(None, description="Main image URL")
    logo_url: Optional[str] = Field(None, description="Complex logo URL")
    virtual_tour_url: Optional[str] = Field(None, description="3D virtual tour URL")
    website_url: Optional[str] = Field(None, description="Complex website URL")


class ComplexUpdateRequest(BaseModel):
    """Schema for updating complex information."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Complex name")
    description: Optional[str] = Field(None, min_length=10, description="Complex description")
    complex_class: Optional[ComplexClass] = Field(None, description="Complex class")
    
    # Location (usually not updated)
    district: Optional[str] = Field(None, max_length=100, description="District")
    address: Optional[str] = Field(None, min_length=5, max_length=500, description="Full address")
    
    # Coordinates
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    
    # Construction information
    status: Optional[ComplexStatus] = Field(None, description="Complex status")
    construction_start_date: Optional[date] = Field(None, description="Construction start date")
    planned_completion_date: Optional[date] = Field(None, description="Planned completion date")
    actual_completion_date: Optional[date] = Field(None, description="Actual completion date")
    
    # Buildings information
    total_buildings: Optional[int] = Field(None, ge=1, description="Total number of buildings")
    total_apartments: Optional[int] = Field(None, ge=1, description="Total number of apartments")
    
    # Price information
    price_from: Optional[Decimal] = Field(None, ge=0, description="Starting price")
    price_to: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    
    # Infrastructure
    has_parking: Optional[bool] = Field(None, description="Has parking")
    has_playground: Optional[bool] = Field(None, description="Has playground")
    has_school: Optional[bool] = Field(None, description="Has school nearby")
    has_kindergarten: Optional[bool] = Field(None, description="Has kindergarten nearby")
    has_shopping_center: Optional[bool] = Field(None, description="Has shopping center nearby")
    has_fitness_center: Optional[bool] = Field(None, description="Has fitness center")
    has_concierge: Optional[bool] = Field(None, description="Has concierge service")
    has_security: Optional[bool] = Field(None, description="Has security")
    
    # Features
    is_featured: Optional[bool] = Field(None, description="Featured complex")
    
    # Media
    main_image_url: Optional[str] = Field(None, description="Main image URL")
    logo_url: Optional[str] = Field(None, description="Complex logo URL")
    virtual_tour_url: Optional[str] = Field(None, description="3D virtual tour URL")
    website_url: Optional[str] = Field(None, description="Complex website URL")


class ComplexImageResponse(BaseModel):
    """Schema for complex image information."""
    
    id: UUID
    url: str
    title: Optional[str]
    description: Optional[str]
    order: int
    is_main: bool
    width: Optional[int]
    height: Optional[int]
    
    class Config:
        from_attributes = True


class DeveloperBasicInfo(BaseModel):
    """Basic developer information for complex responses."""
    
    id: UUID
    company_name: str
    legal_name: str
    is_verified: bool
    rating: Decimal
    reviews_count: int
    
    class Config:
        from_attributes = True


class ComplexListResponse(BaseModel):
    """Schema for complex list items."""
    
    id: UUID
    name: str
    complex_class: ComplexClass
    status: ComplexStatus
    
    # Location
    region: str
    city: str
    district: Optional[str]
    full_address: str
    
    # Price information
    price_from: Optional[Decimal]
    price_to: Optional[Decimal]
    
    # Key features
    has_parking: bool
    has_playground: bool
    has_school: bool
    has_kindergarten: bool
    
    # Media
    main_image_url: Optional[str]
    
    # Developer
    developer: DeveloperBasicInfo
    
    # Statistics
    properties_count: int = Field(default=0, description="Number of properties")
    completion_progress: Optional[int] = Field(description="Completion progress percentage")
    
    # Dates
    construction_start_date: Optional[date]
    planned_completion_date: Optional[date]
    created_at: str
    
    class Config:
        from_attributes = True


class ComplexResponse(ComplexListResponse):
    """Schema for detailed complex information."""
    
    description: str
    
    # Coordinates
    latitude: Optional[float]
    longitude: Optional[float]
    
    # Buildings information
    total_buildings: Optional[int]
    total_apartments: Optional[int]
    
    # All infrastructure features
    has_shopping_center: bool
    has_fitness_center: bool
    has_concierge: bool
    has_security: bool
    
    # Features
    is_featured: bool
    
    # Media
    logo_url: Optional[str]
    virtual_tour_url: Optional[str]
    website_url: Optional[str]
    
    # Images
    images: List[ComplexImageResponse] = Field(default_factory=list)
    
    # Additional dates
    actual_completion_date: Optional[date]
    updated_at: str
    
    class Config:
        from_attributes = True


class ComplexSearchParams(BaseModel):
    """Schema for complex search parameters."""
    
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    # Filters
    complex_class: Optional[str] = None
    status: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    developer_id: Optional[str] = None
    developer_verified: Optional[bool] = None
    is_featured: Optional[bool] = None
    
    # Infrastructure filters
    has_parking: Optional[bool] = None
    has_playground: Optional[bool] = None
    has_school: Optional[bool] = None
    has_kindergarten: Optional[bool] = None
    has_shopping_center: Optional[bool] = None
    has_fitness_center: Optional[bool] = None
    
    # Date filters
    construction_year_from: Optional[int] = None
    construction_year_to: Optional[int] = None
    completion_year_from: Optional[int] = None
    completion_year_to: Optional[int] = None
    
    # Sorting and search
    sort: str = Field(default="created_desc")
    search: Optional[str] = None
    
    # Geographic search
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius: Optional[int] = None


class ComplexSearchResponse(BaseModel):
    """Schema for complex search results."""
    
    items: List[ComplexListResponse]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool
    
    # Search metadata
    filters_applied: dict
    sort_applied: str
    search_query: Optional[str] = None
