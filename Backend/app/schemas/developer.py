"""
Developer-specific schemas for registration and management.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.developer import VerificationStatus


class DeveloperRegisterRequest(BaseModel):
    """Request schema for developer registration."""

    # User information (will create User account with DEVELOPER role)
    phone: str = Field(
        ...,
        description="Company contact phone in international format (+7XXXXXXXXXX)",
        example="+79999999999",
    )
    email: str = Field(..., description="Company contact email", example="info@pik.ru")
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact person first name",
        example="Иван",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact person last name",
        example="Петров",
    )
    middle_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Contact person middle name (optional)",
        example="Сергеевич",
    )

    # Company information
    company_name: str = Field(
        ..., min_length=1, max_length=255, description="Company name", example="ПИК"
    )
    legal_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Legal company name",
        example='ПАО "ПИК-специализированный застройщик"',
    )
    inn: str = Field(
        ..., description="INN (Tax ID) - 10 or 12 digits", example="7704217201"
    )
    ogrn: str = Field(
        ..., description="OGRN - 13 or 15 digits", example="1027700155967"
    )
    legal_address: str = Field(
        ...,
        min_length=10,
        description="Legal address",
        example="123456, г. Москва, ул. Ленина, д. 1",
    )

    # Contact information
    contact_phone: str = Field(
        ..., description="Company contact phone", example="+74951234567"
    )
    contact_email: str = Field(
        ..., description="Company contact email", example="info@pik.ru"
    )
    website: Optional[str] = Field(
        None, description="Company website", example="https://pik.ru"
    )
    description: Optional[str] = Field(
        None,
        description="Company description",
        example="Крупнейший девелопер России, специализирующийся на жилой недвижимости",
    )

    @validator("phone")
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Phone number must be in format +7XXXXXXXXXX")
        return v

    @validator("email", "contact_email")
    def validate_email(cls, v):
        """Validate email format."""
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v

    @validator("inn")
    def validate_inn(cls, v):
        """Validate INN format."""
        if not re.match(r"^\d{10}$|^\d{12}$", v):
            raise ValueError("INN must be 10 or 12 digits")
        return v

    @validator("ogrn")
    def validate_ogrn(cls, v):
        """Validate OGRN format."""
        if not re.match(r"^\d{13}$|^\d{15}$", v):
            raise ValueError("OGRN must be 13 or 15 digits")
        return v

    @validator("website")
    def validate_website(cls, v):
        """Validate website URL."""
        if v and not re.match(r"^https?://.+", v):
            raise ValueError("Website must start with http:// or https://")
        return v


class DeveloperUpdateRequest(BaseModel):
    """Request schema for developer profile updates."""

    company_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Company name"
    )
    contact_phone: Optional[str] = Field(None, description="Company contact phone")
    contact_email: Optional[str] = Field(None, description="Company contact email")
    website: Optional[str] = Field(None, description="Company website")
    description: Optional[str] = Field(None, description="Company description")

    @validator("contact_email")
    def validate_email(cls, v):
        """Validate email format."""
        if v and not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v

    @validator("website")
    def validate_website(cls, v):
        """Validate website URL."""
        if v and not re.match(r"^https?://.+", v):
            raise ValueError("Website must start with http:// or https://")
        return v


class DeveloperResponse(BaseModel):
    """Response schema for developer information."""

    id: UUID = Field(
        ..., description="Developer ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    user_id: UUID = Field(
        ...,
        description="Associated user ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    )

    # Company information
    company_name: str = Field(..., description="Company name", example="ПИК")
    legal_name: str = Field(
        ...,
        description="Legal company name",
        example='ПАО "ПИК-специализированный застройщик"',
    )
    inn: str = Field(..., description="INN (Tax ID)", example="7704217201")
    ogrn: str = Field(..., description="OGRN", example="1027700155967")
    legal_address: str = Field(..., description="Legal address")

    # Contact information
    contact_phone: str = Field(..., description="Company contact phone")
    contact_email: str = Field(..., description="Company contact email")
    website: Optional[str] = Field(None, description="Company website")
    description: Optional[str] = Field(None, description="Company description")
    logo_url: Optional[str] = Field(None, description="Company logo URL")

    # Rating and verification
    rating: Decimal = Field(..., description="Average rating (0-5)", example=4.8)
    reviews_count: int = Field(..., description="Number of reviews", example=156)
    is_verified: bool = Field(..., description="Is developer verified", example=True)
    verification_status: VerificationStatus = Field(
        ..., description="Verification status", example=VerificationStatus.APPROVED
    )

    # Statistics
    properties_count: int = Field(
        default=0, description="Number of properties", example=156
    )
    active_properties_count: int = Field(
        default=0, description="Number of active properties", example=89
    )
    complexes_count: int = Field(
        default=0, description="Number of complexes", example=12
    )

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class DeveloperListResponse(BaseModel):
    """Response schema for developer list."""

    id: UUID
    company_name: str
    logo_url: Optional[str]
    rating: Decimal
    reviews_count: int
    properties_count: int
    is_verified: bool
    verification_status: VerificationStatus
    description: Optional[str]

    class Config:
        from_attributes = True


class DeveloperSearchParams(BaseModel):
    """Search parameters for developers."""

    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    city: Optional[str] = Field(None, description="Filter by city")
    is_verified: Optional[bool] = Field(
        None, description="Filter by verification status"
    )
    rating_min: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    search: Optional[str] = Field(None, description="Search in company name")


class PaginationMeta(BaseModel):
    """Pagination metadata schema."""
    
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number if available")
    prev_page: Optional[int] = Field(None, description="Previous page number if available")


class DeveloperListPaginated(BaseModel):
    """Paginated developer list response schema."""
    
    items: List[DeveloperListResponse] = Field(..., description="List of developers")
    pagination: PaginationMeta = Field(..., description="Pagination information")


class DeveloperVerificationRequest(BaseModel):
    """Request schema for developer verification (admin only)."""

    developer_id: UUID = Field(..., description="Developer ID to verify")
    verification_status: VerificationStatus = Field(
        ..., description="New verification status"
    )
    notes: Optional[str] = Field(None, description="Verification notes")


class DeveloperDashboardResponse(BaseModel):
    """Developer dashboard data response."""
    
    # Overview statistics
    total_properties: int = Field(default=0, description="Total properties count")
    active_properties: int = Field(default=0, description="Active properties count")
    total_complexes: int = Field(default=0, description="Total complexes count")
    total_views: int = Field(default=0, description="Total property views")
    total_contacts: int = Field(default=0, description="Total contact requests")
    total_bookings: int = Field(default=0, description="Total bookings")
    
    # Monthly statistics
    monthly_views: int = Field(default=0, description="Views this month")
    monthly_contacts: int = Field(default=0, description="Contacts this month")
    monthly_bookings: int = Field(default=0, description="Bookings this month")
    
    # Performance metrics
    avg_response_time: Optional[float] = Field(None, description="Average response time in hours")
    conversion_rate: Optional[float] = Field(None, description="Lead to booking conversion rate")
    
    # Recent activity
    recent_properties: List[dict] = Field(default=[], description="Recent properties")
    recent_inquiries: List[dict] = Field(default=[], description="Recent inquiries")
    
    # Trends
    views_trend: Optional[float] = Field(None, description="Views trend percentage")
    contacts_trend: Optional[float] = Field(None, description="Contacts trend percentage")
    bookings_trend: Optional[float] = Field(None, description="Bookings trend percentage")


class DeveloperStatsResponse(BaseModel):
    """Developer statistics response."""
    
    period: str = Field(..., description="Statistics period")
    
    # Property statistics
    properties_stats: dict = Field(default={}, description="Property-related statistics")
    views_stats: dict = Field(default={}, description="Views statistics")
    engagement_stats: dict = Field(default={}, description="Engagement statistics")
    
    # Financial statistics
    revenue_stats: dict = Field(default={}, description="Revenue statistics")
    booking_stats: dict = Field(default={}, description="Booking statistics")
    
    # Performance metrics
    performance_metrics: dict = Field(default={}, description="Performance metrics")
    
    # Charts data
    charts_data: dict = Field(default={}, description="Data for charts and graphs")


class DeveloperCreateByAdminRequest(BaseModel):
    """Request schema for creating developer by admin (no SMS verification)."""
    
    # User information
    phone: str = Field(
        ...,
        description="Company contact phone in international format (+7XXXXXXXXXX)",
        example="+79999999999",
    )
    email: str = Field(..., description="Company contact email", example="info@pik.ru")
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact person first name",
        example="Иван",
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Contact person last name",
        example="Петров",
    )
    middle_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Contact person middle name (optional)",
        example="Сергеевич",
    )
    
    # Company information
    company_name: str = Field(
        ..., min_length=1, max_length=255, description="Company name", example="ПИК"
    )
    legal_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Legal company name",
        example='ПАО "ПИК-специализированный застройщик"',
    )
    inn: str = Field(
        ..., description="INN (Tax ID) - 10 or 12 digits", example="7704217201"
    )
    ogrn: str = Field(
        ..., description="OGRN - 13 or 15 digits", example="1027700155967"
    )
    legal_address: str = Field(
        ...,
        min_length=10,
        description="Legal address",
        example="123456, г. Москва, ул. Ленина, д. 1",
    )
    
    # Contact information
    contact_phone: str = Field(
        ..., description="Company contact phone", example="+74951234567"
    )
    contact_email: str = Field(
        ..., description="Company contact email", example="info@pik.ru"
    )
    website: Optional[str] = Field(
        None, description="Company website", example="https://pik.ru"
    )
    description: Optional[str] = Field(
        None,
        description="Company description",
        example="Крупнейший девелопер России, специализирующийся на жилой недвижимости",
    )
    
    # Admin options
    password: str = Field(
        ..., 
        min_length=8, 
        description="Initial password for developer account",
        example="SecurePassword123!"
    )
    verification_status: VerificationStatus = Field(
        default=VerificationStatus.APPROVED, 
        description="Initial verification status"
    )
    is_verified: bool = Field(
        default=True, 
        description="Whether developer is initially verified"
    )
    
    @validator("phone")
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Phone number must be in format +7XXXXXXXXXX")
        return v
    
    @validator("email", "contact_email")
    def validate_email(cls, v):
        """Validate email format."""
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v
    
    @validator("inn")
    def validate_inn(cls, v):
        """Validate INN format."""
        if not re.match(r"^\d{10}$|^\d{12}$", v):
            raise ValueError("INN must be 10 or 12 digits")
        return v
    
    @validator("ogrn")
    def validate_ogrn(cls, v):
        """Validate OGRN format."""
        if not re.match(r"^\d{13}$|^\d{15}$", v):
            raise ValueError("OGRN must be 13 or 15 digits")
        return v
    
    @validator("website")
    def validate_website(cls, v):
        """Validate website URL."""
        if v and not re.match(r"^https?://.+", v):
            raise ValueError("Website must start with http:// or https://")
        return v


class DeveloperLoginRequest(BaseModel):
    """Request schema for developer login."""
    
    email: str = Field(..., description="Developer email", example="info@pik.ru")
    password: str = Field(..., description="Developer password")
    
    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v


class DeveloperPasswordChangeRequest(BaseModel):
    """Request schema for developer password change."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ..., 
        min_length=8, 
        description="New password (min 8 characters)"
    )
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
