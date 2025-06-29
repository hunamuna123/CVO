"""
Authentication schemas for request and response validation.
"""

import re
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.models.user import UserRole


class PhoneRegisterRequest(BaseModel):
    """Request schema for phone-based registration."""

    phone: str = Field(
        ...,
        description="Phone number in international format (+7XXXXXXXXXX)",
        example="+79999999999",
    )
    first_name: str = Field(
        ..., min_length=1, max_length=100, description="First name", example="Иван"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="Last name", example="Петров"
    )
    middle_name: Optional[str] = Field(
        None, max_length=100, description="Middle name (optional)", example="Сергеевич"
    )
    email: Optional[str] = Field(
        None, description="Email address (optional)", example="ivan@example.com"
    )

    @validator("phone")
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Phone number must be in format +7XXXXXXXXXX")
        return v

    @validator("email")
    def validate_email(cls, v):
        """Validate email format."""
        if v and not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format")
        return v


class PhoneLoginRequest(BaseModel):
    """Request schema for phone-based login."""

    phone: str = Field(
        ...,
        description="Phone number in international format (+7XXXXXXXXXX)",
        example="+79999999999",
    )

    @validator("phone")
    def validate_phone(cls, v):
        """Validate phone number format."""
        if not re.match(r"^\+7\d{10}$", v):
            raise ValueError("Phone number must be in format +7XXXXXXXXXX")
        return v


class VerificationRequest(BaseModel):
    """Request schema for SMS verification."""

    session_id: str = Field(
        ...,
        description="Verification session ID",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    verification_code: str = Field(
        ...,
        min_length=4,
        max_length=4,
        description="4-digit verification code",
        example="1234",
    )

    @validator("verification_code")
    def validate_code(cls, v):
        """Validate verification code format."""
        if not re.match(r"^\d{4}$", v):
            raise ValueError("Verification code must be 4 digits")
        return v


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(
        ...,
        description="Refresh token",
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    )


class AuthResponse(BaseModel):
    """Response schema for successful authentication."""

    message: str = Field(
        ..., description="Response message", example="SMS с кодом отправлен"
    )
    session_id: str = Field(
        ...,
        description="Session ID for verification",
        example="550e8400-e29b-41d4-a716-446655440000",
    )


class TokenResponse(BaseModel):
    """Response schema for token generation."""

    access_token: str = Field(
        ...,
        description="JWT access token",
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token",
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    )
    token_type: str = Field(
        default="Bearer", description="Token type", example="Bearer"
    )
    user: "UserResponse" = Field(..., description="User information")


class RefreshResponse(BaseModel):
    """Response schema for token refresh."""

    access_token: str = Field(
        ...,
        description="New JWT access token",
        example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    )
    token_type: str = Field(
        default="Bearer", description="Token type", example="Bearer"
    )


class UserResponse(BaseModel):
    """Response schema for user information."""

    id: UUID = Field(
        ..., description="User ID", example="550e8400-e29b-41d4-a716-446655440000"
    )
    phone: str = Field(..., description="Phone number", example="+79999999999")
    email: Optional[str] = Field(
        None, description="Email address", example="ivan@example.com"
    )
    first_name: str = Field(..., description="First name", example="Иван")
    last_name: str = Field(..., description="Last name", example="Петров")
    middle_name: Optional[str] = Field(
        None, description="Middle name", example="Сергеевич"
    )
    role: UserRole = Field(..., description="User role", example=UserRole.USER)
    is_active: bool = Field(..., description="Is user active", example=True)
    is_verified: bool = Field(..., description="Is phone verified", example=True)
    avatar_url: Optional[str] = Field(
        None, description="Avatar URL", example="https://example.com/avatar.jpg"
    )
    created_at: str = Field(
        ..., description="Creation timestamp", example="2023-01-01T00:00:00Z"
    )

    class Config:
        from_attributes = True


# Circular import resolution
TokenResponse.model_rebuild()
