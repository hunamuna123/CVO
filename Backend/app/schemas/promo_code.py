"""
Promo code schemas for API requests and responses.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.promo_code import PromoCodeStatus, PromoCodeType


# Base schemas
class PromoCodeBase(BaseModel):
    """Base promo code schema."""
    
    code: str = Field(..., min_length=3, max_length=50, description="Promo code")
    title: str = Field(..., min_length=1, max_length=255, description="Promo code title")
    description: Optional[str] = Field(None, description="Promo code description")
    promo_type: PromoCodeType = Field(..., description="Promo code type")


class PromoCodeCreateRequest(PromoCodeBase):
    """Schema for creating a new promo code."""
    
    # Discount information
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Discount percentage (0-100)")
    discount_amount: Optional[Decimal] = Field(None, ge=0, description="Fixed discount amount")
    max_discount_amount: Optional[Decimal] = Field(None, ge=0, description="Maximum discount amount for percentage codes")
    
    # Usage limits
    usage_limit: Optional[int] = Field(None, ge=1, description="Total usage limit (null = unlimited)")
    usage_limit_per_user: Optional[int] = Field(default=1, ge=1, description="Usage limit per user")
    
    # Minimum order requirements
    min_order_amount: Optional[Decimal] = Field(None, ge=0, description="Minimum order amount")
    
    # Validity period
    valid_from: date = Field(..., description="Valid from date")
    valid_until: date = Field(..., description="Valid until date")
    
    # Targeting
    for_new_users_only: bool = Field(default=False, description="Only for new users")
    
    # Specific targeting
    target_property_id: Optional[UUID] = Field(None, description="Target specific property")
    target_complex_id: Optional[UUID] = Field(None, description="Target specific complex")
    
    # Geographic targeting
    target_city: Optional[str] = Field(None, description="Target specific city")
    target_region: Optional[str] = Field(None, description="Target specific region")
    
    @validator('valid_until')
    def validate_validity_period(cls, v, values):
        """Validate that valid_until is after valid_from."""
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError('valid_until must be after valid_from')
        return v
    
    @validator('discount_percentage')
    def validate_percentage_discount(cls, v, values):
        """Validate percentage discount based on promo type."""
        if values.get('promo_type') == PromoCodeType.PERCENTAGE and v is None:
            raise ValueError('discount_percentage is required for PERCENTAGE type')
        if values.get('promo_type') != PromoCodeType.PERCENTAGE and v is not None:
            raise ValueError('discount_percentage should only be set for PERCENTAGE type')
        return v
    
    @validator('discount_amount')
    def validate_amount_discount(cls, v, values):
        """Validate amount discount based on promo type."""
        if values.get('promo_type') in [PromoCodeType.FIXED_AMOUNT, PromoCodeType.CASHBACK] and v is None:
            raise ValueError('discount_amount is required for FIXED_AMOUNT and CASHBACK types')
        if values.get('promo_type') == PromoCodeType.PERCENTAGE and v is not None:
            raise ValueError('discount_amount should not be set for PERCENTAGE type')
        return v


class PromoCodeUpdateRequest(BaseModel):
    """Schema for updating promo code information."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Promo code title")
    description: Optional[str] = Field(None, description="Promo code description")
    
    # Usage limits (can be updated)
    usage_limit: Optional[int] = Field(None, ge=1, description="Total usage limit")
    usage_limit_per_user: Optional[int] = Field(None, ge=1, description="Usage limit per user")
    
    # Validity period (can extend, but not shorten if already active)
    valid_until: Optional[date] = Field(None, description="Valid until date")
    
    # Targeting
    for_new_users_only: Optional[bool] = Field(None, description="Only for new users")
    target_property_id: Optional[UUID] = Field(None, description="Target specific property")
    target_complex_id: Optional[UUID] = Field(None, description="Target specific complex")
    target_city: Optional[str] = Field(None, description="Target specific city")
    target_region: Optional[str] = Field(None, description="Target specific region")


class PromoCodeValidationRequest(BaseModel):
    """Schema for validating a promo code."""
    
    code: str = Field(..., description="Promo code to validate")
    property_id: UUID = Field(..., description="Property ID for the order")
    order_amount: Decimal = Field(..., ge=0, description="Order amount to calculate discount")


class DeveloperBasicInfo(BaseModel):
    """Basic developer information for promo code responses."""
    
    id: UUID
    company_name: str
    is_verified: bool
    
    class Config:
        from_attributes = True


class PromoCodeListResponse(BaseModel):
    """Schema for promo code list items."""
    
    id: UUID
    code: str
    title: str
    promo_type: PromoCodeType
    status: PromoCodeStatus
    
    # Discount information
    discount_percentage: Optional[Decimal]
    discount_amount: Optional[Decimal]
    max_discount_amount: Optional[Decimal]
    
    # Usage information
    usage_limit: Optional[int]
    used_count: int
    usage_percentage: Optional[float] = Field(description="Usage percentage")
    
    # Validity
    valid_from: date
    valid_until: date
    is_valid: bool = Field(description="Is currently valid")
    is_expired: bool = Field(description="Is expired")
    
    # Developer (if applicable)
    developer: Optional[DeveloperBasicInfo]
    
    # Targeting
    target_city: Optional[str]
    target_region: Optional[str]
    for_new_users_only: bool
    
    # Dates
    created_at: str
    
    class Config:
        from_attributes = True


class PromoCodeResponse(PromoCodeListResponse):
    """Schema for detailed promo code information."""
    
    description: Optional[str]
    
    # Usage limits
    usage_limit_per_user: Optional[int]
    
    # Minimum order requirements
    min_order_amount: Optional[Decimal]
    
    # Specific targeting
    target_property_id: Optional[UUID]
    target_complex_id: Optional[UUID]
    
    # Dates
    updated_at: str
    
    class Config:
        from_attributes = True


class PromoCodeValidationResponse(BaseModel):
    """Schema for promo code validation response."""
    
    is_valid: bool = Field(description="Whether the code is valid")
    error_message: Optional[str] = Field(None, description="Error message if invalid")
    
    # Discount calculation (if valid)
    discount_amount: Optional[Decimal] = Field(None, description="Calculated discount amount")
    final_amount: Optional[Decimal] = Field(None, description="Final amount after discount")
    
    # Promo code details (if valid)
    promo_details: Optional[PromoCodeListResponse] = Field(None, description="Promo code details")


class PromoCodeSearchParams(BaseModel):
    """Schema for promo code search parameters."""
    
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
    # Filters
    promo_type: Optional[str] = None
    status: Optional[str] = None
    developer_id: Optional[str] = None
    is_platform_code: Optional[bool] = None
    target_city: Optional[str] = None
    target_region: Optional[str] = None
    valid_only: Optional[bool] = None
    
    # Sorting and search
    sort: str = Field(default="created_desc")
    search: Optional[str] = None


class PromoCodeSearchResponse(BaseModel):
    """Schema for promo code search results."""
    
    items: list[PromoCodeListResponse]
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
