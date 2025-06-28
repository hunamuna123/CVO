"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    AuthResponse,
    PhoneLoginRequest,
    PhoneRegisterRequest,
    RefreshResponse,
    RefreshTokenRequest,
    TokenResponse,
    VerificationRequest,
)
from app.services.auth_service import AuthService
from app.utils.security import security

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Initialize the auth service
auth_service = AuthService()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Register new user",
    description="Register a new user with phone number and send SMS verification code",
)
async def register(
    request: PhoneRegisterRequest, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Register a new user with phone number.

    - **phone**: Phone number in international format (+7XXXXXXXXXX)
    - **first_name**: User's first name (required)
    - **last_name**: User's last name (required)
    - **middle_name**: User's middle name (optional)
    - **email**: Email address (optional)

    Returns session_id for SMS verification.
    """
    return await auth_service.register(db, request)


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with phone",
    description="Login with phone number and send SMS verification code",
)
async def login(
    request: PhoneLoginRequest, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    Login with phone number.

    - **phone**: Phone number in international format (+7XXXXXXXXXX)

    Returns session_id for SMS verification.
    """
    return await auth_service.login(db, request)


@router.post(
    "/verify",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify SMS code",
    description="Verify SMS code and get access/refresh tokens",
)
async def verify(
    request: VerificationRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Verify SMS code and complete authentication.

    - **session_id**: Session ID from register/login response
    - **verification_code**: 4-digit SMS verification code

    Returns access_token, refresh_token and user information.
    """
    return await auth_service.verify(db, request)


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using refresh token",
)
async def refresh_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> RefreshResponse:
    """
    Refresh access token.

    - **refresh_token**: Valid refresh token

    Returns new access_token.
    """
    return await auth_service.refresh_token(db, request)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout user and invalidate tokens",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user and invalidate tokens.

    Requires valid access token in Authorization header.
    """
    access_token = credentials.credentials
    return await auth_service.logout(db, access_token)
