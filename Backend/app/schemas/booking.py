"""
Booking schemas for API requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.booking import BookingSource, BookingStatus


# Base schemas
class BookingBase(BaseModel):
    """Base booking schema."""
    
    contact_phone: str = Field(..., min_length=10, max_length=20, description="Contact phone")
    contact_email: Optional[str] = Field(None, description="Contact email")
    notes: Optional[str] = Field(None, description="Additional notes")


class BookingCreateRequest(BookingBase):
    """Schema for creating a new booking."""
    
    property_id: UUID = Field(..., description="Property ID to book")
    promo_code: Optional[str] = Field(None, description="Promotional code")
    
    # Tracking parameters
    utm_source: Optional[str] = Field(None, description="UTM source")
    utm_medium: Optional[str] = Field(None, description="UTM medium")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign")


class BookingUpdateRequest(BaseModel):
    """Schema for updating booking information."""
    
    contact_phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Contact phone")
    contact_email: Optional[str] = Field(None, description="Contact email")
    notes: Optional[str] = Field(None, description="Additional notes")
    promo_code: Optional[str] = Field(None, description="Promotional code (if changeable)")


class BookingStatusUpdateRequest(BaseModel):
    """Schema for updating booking status."""
    
    status: BookingStatus = Field(..., description="New booking status")
    notes: Optional[str] = Field(None, description="Status change notes")
    cancellation_reason: Optional[str] = Field(None, description="Cancellation reason (if cancelling)")


class PropertyBasicInfo(BaseModel):
    """Basic property information for booking responses."""
    
    id: UUID
    title: str
    property_type: str
    deal_type: str
    price: Decimal
    full_address: str
    main_image_url: Optional[str]
    
    class Config:
        from_attributes = True


class UserBasicInfo(BaseModel):
    """Basic user information for booking responses."""
    
    id: UUID
    full_name: str
    phone: str
    email: Optional[str]
    
    class Config:
        from_attributes = True


class DeveloperBasicInfo(BaseModel):
    """Basic developer information for booking responses."""
    
    id: UUID
    company_name: str
    contact_phone: str
    contact_email: str
    is_verified: bool
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for booking list items."""
    
    id: UUID
    booking_number: str
    status: BookingStatus
    source: BookingSource
    
    # Pricing
    property_price: Decimal
    discount_amount: Optional[Decimal]
    final_price: Decimal
    
    # Property
    property: PropertyBasicInfo
    
    # User
    user: UserBasicInfo
    
    # Developer
    developer: DeveloperBasicInfo
    
    # Dates
    booking_date: datetime
    expires_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    
    # Contact
    contact_phone: str
    contact_email: Optional[str]
    
    class Config:
        from_attributes = True


class BookingResponse(BookingListResponse):
    """Schema for detailed booking information."""
    
    # Commission
    platform_commission_rate: Optional[Decimal]
    platform_commission_amount: Optional[Decimal]
    
    # All dates
    paid_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Additional information
    notes: Optional[str]
    cancellation_reason: Optional[str]
    promo_code: Optional[str]
    
    # Tracking
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    
    # Calculated properties
    is_active: bool = Field(description="Is booking active")
    is_expired: bool = Field(description="Is booking expired")
    discount_percentage: Optional[Decimal] = Field(description="Discount percentage")
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingSearchParams(BaseModel):
    """Schema for booking search parameters."""
    
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    # Filters
    status: Optional[str] = None
    source: Optional[str] = None
    developer_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    property_id: Optional[UUID] = None
    date_from: Optional[str] = None  # YYYY-MM-DD format
    date_to: Optional[str] = None    # YYYY-MM-DD format
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    promo_code: Optional[str] = None
    
    # Sorting and search
    sort: str = Field(default="created_desc")
    search: Optional[str] = None


class BookingSearchResponse(BaseModel):
    """Schema for booking search results."""
    
    items: list[BookingListResponse]
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
