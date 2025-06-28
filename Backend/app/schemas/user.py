"""
User schemas for profile management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserProfileResponse(BaseModel):
    """User profile response schema."""

    id: str
    phone: str
    email: Optional[str] = None
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdateRequest(BaseModel):
    """User profile update request schema."""

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None


class UserAvatarUploadResponse(BaseModel):
    """User avatar upload response schema."""

    avatar_url: str
    message: str = "Avatar uploaded successfully"


class UserPublicProfileResponse(BaseModel):
    """Public user profile response schema (limited information)."""

    id: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}
