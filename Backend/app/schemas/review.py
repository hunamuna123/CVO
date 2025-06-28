"""
Review-related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ReviewBase(BaseModel):
    """Base review schema."""

    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    title: str = Field(..., min_length=5, max_length=200, description="Review title")
    content: str = Field(..., min_length=10, max_length=2000, description="Review content")


class ReviewCreateRequest(ReviewBase):
    """Schema for creating a review."""

    developer_id: str = Field(..., description="Developer UUID")
    property_id: Optional[str] = Field(None, description="Property UUID (optional)")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        """Validate review content."""
        if len(v.strip()) < 10:
            raise ValueError("Отзыв должен содержать не менее 10 символов")
        return v.strip()


class ReviewUpdateRequest(BaseModel):
    """Schema for updating a review."""

    rating: Optional[int] = Field(None, ge=1, le=5, description="New rating")
    title: Optional[str] = Field(None, min_length=5, max_length=200, description="New title")
    content: Optional[str] = Field(None, min_length=10, max_length=2000, description="New content")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        """Validate review content."""
        if v and len(v.strip()) < 10:
            raise ValueError("Отзыв должен содержать не менее 10 символов")
        return v.strip() if v else v


class ReviewSearchParams(BaseModel):
    """Schema for review search parameters."""

    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    developer_id: Optional[str] = None
    property_id: Optional[str] = None
    rating_min: Optional[int] = Field(None, ge=1, le=5)
    rating_max: Optional[int] = Field(None, ge=1, le=5)
    is_verified: Optional[bool] = None
    sort: str = Field("created_desc")


class UserInfo(BaseModel):
    """User information for reviews."""

    id: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None


class DeveloperInfo(BaseModel):
    """Developer information for reviews."""

    id: str
    company_name: str
    logo_url: Optional[str] = None


class PropertyInfo(BaseModel):
    """Property information for reviews."""

    id: str
    title: str
    property_type: str


class ReviewResponse(ReviewBase):
    """Schema for review response."""

    id: str
    user_id: str
    developer_id: str
    property_id: Optional[str]
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    # Related entities
    user: UserInfo
    developer: DeveloperInfo
    property: Optional[PropertyInfo] = None

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Schema for review list item."""

    id: str
    rating: int
    title: str
    content: str
    is_verified: bool
    created_at: datetime
    
    # Basic user info
    user: UserInfo
    
    # Basic developer/property info
    developer: DeveloperInfo
    property: Optional[PropertyInfo] = None

    class Config:
        from_attributes = True
