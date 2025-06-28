"""
User API endpoints for profile management.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import User
from app.schemas.user import (
    UserAvatarUploadResponse,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserPublicProfileResponse,
)
from app.services.user_service import UserService
from app.services.file_service import FileService
from app.repositories.user_repository import UserRepository
from app.utils.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Get UserService instance with dependencies."""
    user_repository = UserRepository(db)
    file_service = FileService()
    return UserService(user_repository, file_service)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get current user profile",
    description="Get the current user's profile information",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> UserProfileResponse:
    """
    Get current user's profile.

    **Requirements:**
    - Valid access token in Authorization header

    Returns complete user profile information including:
    - Personal information (name, email, phone)
    - Account status and role
    - Avatar URL
    - Account creation and update timestamps
    """
    return await user_service.get_user_profile(db, str(current_user.id))


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Update current user profile",
    description="Update the current user's profile information",
)
async def update_my_profile(
    profile_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> UserProfileResponse:
    """
    Update current user's profile.

    **Requirements:**
    - Valid access token in Authorization header

    **Updatable fields:**
    - **first_name**: First name (1-100 characters)
    - **last_name**: Last name (1-100 characters)
    - **middle_name**: Middle name (optional, max 100 characters)
    - **email**: Email address (optional, must be valid email)

    **Note:**
    - Phone number cannot be changed through this endpoint
    - Role and verification status are managed by administrators
    - Email changes may require re-verification
    """
    return await user_service.update_user_profile(
        db, str(current_user.id), profile_data
    )


@router.post(
    "/me/avatar",
    response_model=UserAvatarUploadResponse,
    summary="Upload user avatar",
    description="Upload or update the current user's avatar image",
)
async def upload_my_avatar(
    file: UploadFile = File(..., description="Avatar image file"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> UserAvatarUploadResponse:
    """
    Upload or update user avatar.

    **Requirements:**
    - Valid access token in Authorization header

    **File requirements:**
    - Supported formats: JPG, JPEG, PNG, WebP
    - Maximum file size: 50MB
    - Image will be automatically resized to 500x500 pixels
    - Converted to WebP format for optimization

    **Features:**
    - Automatic image optimization and compression
    - Old avatar is automatically deleted when uploading new one
    - Square crop with proper aspect ratio handling

    **Form data:**
    - **file**: Image file to upload

    Returns the new avatar URL for immediate use.
    """
    avatar_url = await user_service.upload_user_avatar(db, str(current_user.id), file)

    return UserAvatarUploadResponse(avatar_url=avatar_url)


@router.delete(
    "/me/avatar",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user avatar",
    description="Delete the current user's avatar image",
)
async def delete_my_avatar(
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete current user's avatar.

    **Requirements:**
    - Valid access token in Authorization header

    **Warning:** This action cannot be undone.
    The avatar image will be permanently deleted from storage.

    After deletion, the user's profile will show no avatar image.
    """
    await user_service.delete_user_avatar(db, str(current_user.id))

    return {"message": "Avatar deleted successfully"}


@router.get(
    "/{user_id}",
    response_model=UserPublicProfileResponse,
    summary="Get public user profile",
    description="Get public profile information for any user",
)
async def get_user_public_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> UserPublicProfileResponse:
    """
    Get public user profile by ID.

    **Path parameters:**
    - **user_id**: User UUID

    Returns limited public profile information:
    - First and last name
    - Avatar image
    - User role
    - Account creation date

    **Privacy:**
    - Private information (phone, email) is not included
    - Only active users can be viewed
    - Some users may have restricted public profiles

    **Use cases:**
    - Displaying user information in reviews
    - Showing property contact information
    - User discovery and networking
    """
    return await user_service.get_public_profile(db, user_id)
