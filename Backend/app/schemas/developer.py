"""
Developer-specific schemas for registration and management.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

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

    id: str = Field(
        ..., description="Developer ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    user_id: str = Field(
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

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class DeveloperListResponse(BaseModel):
    """Response schema for developer list."""

    id: str
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


class DeveloperVerificationRequest(BaseModel):
    """Request schema for developer verification (admin only)."""

    developer_id: str = Field(..., description="Developer ID to verify")
    verification_status: VerificationStatus = Field(
        ..., description="New verification status"
    )
    notes: Optional[str] = Field(None, description="Verification notes")
