"""
Lead-related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator
import phonenumbers


class LeadBase(BaseModel):
    """Base lead schema."""

    name: str = Field(..., min_length=2, max_length=100, description="Contact person name")
    phone: str = Field(..., description="Contact phone number")
    email: Optional[str] = Field(None, description="Contact email")
    message: Optional[str] = Field(None, max_length=1000, description="Additional message")
    lead_type: str = Field(..., description="Lead type: CALL_REQUEST, VIEWING, CONSULTATION")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number."""
        try:
            parsed = phonenumbers.parse(v, "RU")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Некорректный номер телефона")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Некорректный формат номера телефона")

    @field_validator("lead_type")
    @classmethod
    def validate_lead_type(cls, v):
        """Validate lead type."""
        valid_types = ["CALL_REQUEST", "VIEWING", "CONSULTATION"]
        if v not in valid_types:
            raise ValueError(f"Недопустимый тип заявки. Доступные: {', '.join(valid_types)}")
        return v


class LeadCreateRequest(LeadBase):
    """Schema for creating a lead."""

    property_id: str = Field(..., description="Property UUID")


class LeadStatusUpdateRequest(BaseModel):
    """Schema for updating lead status."""

    status: str = Field(..., description="New status: NEW, IN_PROGRESS, COMPLETED, CANCELLED")
    notes: Optional[str] = Field(None, max_length=500, description="Notes about status change")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate lead status."""
        valid_statuses = ["NEW", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
        if v not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Доступные: {', '.join(valid_statuses)}")
        return v


class LeadSearchParams(BaseModel):
    """Schema for lead search parameters."""

    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    property_id: Optional[str] = None
    lead_type: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort: str = Field("created_desc")


class PropertyInfo(BaseModel):
    """Property information for leads."""

    id: str
    title: str
    property_type: str
    price: Optional[float] = None
    city: str
    street: str


class UserInfo(BaseModel):
    """User information for leads."""

    id: str
    first_name: str
    last_name: str
    email: Optional[str] = None


class LeadResponse(LeadBase):
    """Schema for lead response."""

    id: str
    property_id: str
    user_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    # Related entities
    property: PropertyInfo
    user: Optional[UserInfo] = None

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    """Schema for lead list item."""

    id: str
    name: str
    phone: str
    email: Optional[str]
    lead_type: str
    status: str
    created_at: datetime
    
    # Basic property info
    property: PropertyInfo
    
    # Basic user info (if available)
    user: Optional[UserInfo] = None

    class Config:
        from_attributes = True
