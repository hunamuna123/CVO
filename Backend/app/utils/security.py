"""
Security utilities for authentication and authorization.
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserRole
from app.services.jwt_service import jwt_service

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    """
    try:
        token = credentials.credentials
        user = await jwt_service.get_user_from_token(db, token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Недействительный токен авторизации",
                        "details": {},
                    }
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTHENTICATION_ERROR",
                    "message": "Ошибка аутентификации",
                    "details": {},
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "USER_INACTIVE",
                    "message": "Пользователь деактивирован",
                    "details": {},
                }
            },
        )

    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current verified user.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "USER_NOT_VERIFIED",
                    "message": "Номер телефона не подтвержден",
                    "details": {},
                }
            },
        )

    return current_user


async def get_current_developer_user(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """
    Get current user with developer role.
    """
    if current_user.role != UserRole.DEVELOPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Доступ только для застройщиков",
                    "details": {},
                }
            },
        )

    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """
    Get current user with admin role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Доступ только для администраторов",
                    "details": {},
                }
            },
        )

    return current_user


async def get_current_developer_or_admin_user(
    current_user: User = Depends(get_current_verified_user),
) -> User:
    """
    Get current user with developer or admin role.
    """
    if current_user.role not in [UserRole.DEVELOPER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Доступ только для застройщиков и администраторов",
                    "details": {},
                }
            },
        )

    return current_user


# Optional authentication (for endpoints that work with both authenticated and anonymous users)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user = await jwt_service.get_user_from_token(db, token)
        return user
    except Exception:
        return None


def require_roles(*roles: UserRole):
    """
    Decorator for requiring specific roles.
    """

    def decorator(func):
        async def wrapper(
            current_user: User = Depends(get_current_verified_user), *args, **kwargs
        ):
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "INSUFFICIENT_PERMISSIONS",
                            "message": f"Доступ только для: {', '.join([role.value for role in roles])}",
                            "details": {},
                        }
                    },
                )
            return await func(current_user=current_user, *args, **kwargs)

        return wrapper

    return decorator


def require_owner_or_admin(get_resource_owner_id):
    """
    Decorator for requiring resource ownership or admin role.

    Args:
        get_resource_owner_id: Function that returns the owner ID of the resource
    """

    def decorator(func):
        async def wrapper(
            current_user: User = Depends(get_current_verified_user), *args, **kwargs
        ):
            # Get resource owner ID
            resource_owner_id = await get_resource_owner_id(*args, **kwargs)

            # Allow if admin or owner
            if (
                current_user.role == UserRole.ADMIN
                or current_user.id == resource_owner_id
            ):
                return await func(current_user=current_user, *args, **kwargs)

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "INSUFFICIENT_PERMISSIONS",
                        "message": "Доступ только владельцу ресурса или администратору",
                        "details": {},
                    }
                },
            )

        return wrapper

    return decorator
