"""
User service for profile management and user operations.

This service implements business logic for user management,
using repository pattern for data access and proper dependency injection.
"""

import structlog
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import ServiceBase, with_transaction
from app.repositories.user_repository import IUserRepository, UserRepository
from app.models.user import User, UserRole
from app.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserPublicProfileResponse,
)
from app.services.file_service import FileService
from app.core.exceptions import (
    NotFoundError, 
    ValidationError, 
    BusinessLogicError
)

logger = structlog.get_logger(__name__)


class IUserService:
    """User service interface."""
    
    async def get_user_profile(self, user_id: UUID) -> UserProfileResponse:
        """Get user profile by ID."""
        pass
    
    async def update_user_profile(
        self, 
        user_id: UUID, 
        profile_data: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        """Update user profile."""
        pass
    
    async def upload_user_avatar(self, user_id: UUID, file: UploadFile) -> str:
        """Upload user avatar."""
        pass
    
    async def delete_user_avatar(self, user_id: UUID) -> bool:
        """Delete user avatar."""
        pass
    
    async def get_public_profile(self, user_id: UUID) -> UserPublicProfileResponse:
        """Get public user profile."""
        pass


class UserService(ServiceBase, IUserService):
    """Service for user profile management."""

    def __init__(self, user_repository: IUserRepository, file_service: FileService):
        self.user_repository = user_repository
        self.file_service = file_service

    async def get_user_profile(
        self, db: AsyncSession, user_id: str
    ) -> UserProfileResponse:
        """Get user profile by ID."""
        try:
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "message": "Пользователь не найден",
                            "details": {},
                        }
                    },
                )

            return UserProfileResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to get user profile",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PROFILE_RETRIEVAL_FAILED",
                        "message": "Не удалось получить профиль пользователя",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def update_user_profile(
        self, db: AsyncSession, user_id: str, profile_data: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        """Update user profile."""
        try:
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "message": "Пользователь не найден",
                            "details": {},
                        }
                    },
                )

            # Update fields
            update_data = profile_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)

            await db.commit()
            await db.refresh(user)

            logger.info(
                "User profile updated successfully",
                user_id=user_id,
                updated_fields=list(update_data.keys()),
            )

            return UserProfileResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to update user profile",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PROFILE_UPDATE_FAILED",
                        "message": "Не удалось обновить профиль пользователя",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def upload_user_avatar(
        self, db: AsyncSession, user_id: str, file: UploadFile
    ) -> str:
        """Upload user avatar."""
        try:
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "message": "Пользователь не найден",
                            "details": {},
                        }
                    },
                )

            # Delete old avatar if exists
            if user.avatar_url:
                await self.file_service.delete_file(user.avatar_url)

            # Upload new avatar
            avatar_url = await self.file_service.upload_user_avatar(file, user_id)

            # Update user record
            user.avatar_url = avatar_url
            await db.commit()

            logger.info(
                "User avatar uploaded successfully",
                user_id=user_id,
                avatar_url=avatar_url,
            )

            return avatar_url

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to upload user avatar",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "AVATAR_UPLOAD_FAILED",
                        "message": "Не удалось загрузить аватар",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def delete_user_avatar(self, db: AsyncSession, user_id: str) -> bool:
        """Delete user avatar."""
        try:
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "message": "Пользователь не найден",
                            "details": {},
                        }
                    },
                )

            if not user.avatar_url:
                return True  # Nothing to delete

            # Delete file
            await self.file_service.delete_file(user.avatar_url)

            # Update user record
            user.avatar_url = None
            await db.commit()

            logger.info("User avatar deleted successfully", user_id=user_id)

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to delete user avatar",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "AVATAR_DELETION_FAILED",
                        "message": "Не удалось удалить аватар",
                        "details": {"error": str(e)},
                    }
                },
            )

    async def get_public_profile(
        self, db: AsyncSession, user_id: str
    ) -> UserPublicProfileResponse:
        """Get public user profile (limited information)."""
        try:
            query = select(User).where(User.id == user_id)
            result = await db.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "message": "Пользователь не найден",
                            "details": {},
                        }
                    },
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "USER_INACTIVE",
                            "message": "Профиль пользователя недоступен",
                            "details": {},
                        }
                    },
                )

            return UserPublicProfileResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to get public user profile",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "PUBLIC_PROFILE_RETRIEVAL_FAILED",
                        "message": "Не удалось получить публичный профиль",
                        "details": {"error": str(e)},
                    }
                },
            )
