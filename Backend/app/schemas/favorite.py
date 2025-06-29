"""
Favorite-related Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FavoriteCreateRequest(BaseModel):
    """Schema for creating a favorite."""

    property_id: UUID = Field(..., description="Property UUID")


class PropertyInfo(BaseModel):
    """Property information for favorites."""

    id: UUID
    title: str
    price: Optional[float] = None
    city: str
    property_type: str
    total_area: Optional[float] = None
    rooms_count: Optional[int] = None
    main_image_url: Optional[str] = None
    developer: Optional[dict] = None


class FavoriteResponse(BaseModel):
    """Schema for favorite response."""

    id: UUID
    user_id: UUID

    property_id: UUID

    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    """Schema for favorite list item."""

    id: UUID
    property_id: UUID
    created_at: datetime
    property: PropertyInfo

    class Config:
        from_attributes = True
