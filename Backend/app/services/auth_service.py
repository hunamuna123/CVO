"""
Authentication services for handling registration, login, and token management.
"""

from typing import Union
from uuid import uuid4

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole
from app.schemas.auth import (
    AuthResponse,
    PhoneLoginRequest,
    PhoneRegisterRequest,
    RefreshResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
    VerificationRequest,
)
from app.services.jwt_service import jwt_service
from app.services.sms_service import sms_service

logger = structlog.get_logger(__name__)


class AuthService:
    """
    Service class for authentication-related operations.
    """

    async def register(
        self, db: AsyncSession, request: PhoneRegisterRequest
    ) -> AuthResponse:
        """
        Register a new user with a phone number.
        """
        try:
            # Check if user already exists
            result = await db.execute(select(User).where(User.phone == request.phone))
            existing_user = result.scalar_one_or_none()

            if existing_user:
                logger.warning(
                    "Registration attempt for existing phone", phone=request.phone
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": {
                            "code": "USER_ALREADY_EXISTS",
                            "message": "Пользователь с таким номером телефона уже зарегистрирован",
                            "details": {"phone": request.phone},
                        }
                    },
                )

            # Check if email already exists (if provided)
            if request.email:
                result = await db.execute(
                    select(User).where(User.email == request.email)
                )
                existing_email_user = result.scalar_one_or_none()

                if existing_email_user:
                    logger.warning(
                        "Registration attempt with existing email", email=request.email
                    )
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "error": {
                                "code": "EMAIL_ALREADY_EXISTS",
                                "message": "Пользователь с таким email уже зарегистрирован",
                                "details": {"email": request.email},
                            }
                        },
                    )

            # Create new user (not verified yet)
            new_user = User(
                phone=request.phone,
                first_name=request.first_name,
                last_name=request.last_name,
                middle_name=request.middle_name,
                email=request.email,
                role=UserRole.USER,
                is_verified=False,  # Will be set to True after SMS verification
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            # Generate session ID and send SMS
            session_id = str(uuid4())

            success = await sms_service.send_verification_code(
                request.phone, session_id
            )
            if not success:
                # Rollback user creation if SMS failed
                await db.delete(new_user)
                await db.commit()

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": {
                            "code": "SMS_SEND_FAILED",
                            "message": "Не удалось отправить SMS с кодом подтверждения",
                            "details": {},
                        }
                    },
                )

            logger.info(
                "User registration initiated",
                phone=request.phone,
                user_id=str(new_user.id),
            )

            return AuthResponse(
                message="SMS с кодом подтверждения отправлен", session_id=session_id
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Registration error", phone=request.phone, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "REGISTRATION_ERROR",
                        "message": "Ошибка при регистрации",
                        "details": {},
                    }
                },
            )

    async def login(self, db: AsyncSession, request: PhoneLoginRequest) -> AuthResponse:
        """
        Initiate login procedure for an existing user by sending SMS.
        """
        try:
            # Check if user exists
            result = await db.execute(select(User).where(User.phone == request.phone))
            user = result.scalar_one_or_none()

            if not user:
                logger.warning(
                    "Login attempt for non-existent phone", phone=request.phone
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "message": "Пользователь с таким номером телефона не найден",
                            "details": {"phone": request.phone},
                        }
                    },
                )

            if not user.is_active:
                logger.warning(
                    "Login attempt for inactive user",
                    phone=request.phone,
                    user_id=str(user.id),
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": {
                            "code": "USER_INACTIVE",
                            "message": "Аккаунт деактивирован",
                            "details": {},
                        }
                    },
                )

            # Generate session ID and send SMS
            session_id = str(uuid4())

            success = await sms_service.send_verification_code(
                request.phone, session_id
            )
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": {
                            "code": "SMS_SEND_FAILED",
                            "message": "Не удалось отправить SMS с кодом подтверждения",
                            "details": {},
                        }
                    },
                )

            logger.info(
                "User login initiated", phone=request.phone, user_id=str(user.id)
            )

            return AuthResponse(
                message="SMS с кодом подтверждения отправлен", session_id=session_id
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Login error", phone=request.phone, error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "LOGIN_ERROR",
                        "message": "Ошибка при входе в систему",
                        "details": {},
                    }
                },
            )

    async def verify(
        self, db: AsyncSession, request: VerificationRequest
    ) -> TokenResponse:
        """
        Verify the SMS code and create access/refresh token on success.
        """
        try:
            # Verify SMS code
            phone = await sms_service.verify_code(
                request.session_id, request.verification_code
            )

            if not phone:
                logger.warning(
                    "Invalid verification code", session_id=request.session_id
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": {
                            "code": "INVALID_VERIFICATION_CODE",
                            "message": "Неверный код подтверждения или сессия истекла",
                            "details": {},
                        }
                    },
                )

            # Get user by phone
            result = await db.execute(select(User).where(User.phone == phone))
            user = result.scalar_one_or_none()

            if not user:
                logger.error(
                    "User not found after successful verification", phone=phone
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": {
                            "code": "USER_NOT_FOUND",
                            "message": "Ошибка при поиске пользователя",
                            "details": {},
                        }
                    },
                )

            # Mark user as verified and update
            user.is_verified = True
            await db.commit()
            await db.refresh(user)

            # Create tokens
            tokens = jwt_service.create_token_pair(str(user.id))

            # Create user response
            user_response = UserResponse(
                id=str(user.id),
                phone=user.phone,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                avatar_url=user.avatar_url,
                created_at=user.created_at.isoformat(),
            )

            logger.info(
                "User verified and logged in", phone=phone, user_id=str(user.id)
            )

            return TokenResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type=tokens["token_type"],
                user=user_response,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Verification error", session_id=request.session_id, error=str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "VERIFICATION_ERROR",
                        "message": "Ошибка при подтверждении кода",
                        "details": {},
                    }
                },
            )

    async def refresh_token(
        self, db: AsyncSession, request: RefreshTokenRequest
    ) -> RefreshResponse:
        """
        Refresh the access token using the refresh token.
        """
        try:
            # Verify refresh token
            payload = jwt_service.verify_token(request.refresh_token, "refresh")

            if not payload:
                logger.warning("Invalid refresh token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": {
                            "code": "INVALID_REFRESH_TOKEN",
                            "message": "Недействительный refresh токен",
                            "details": {},
                        }
                    },
                )

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": {
                            "code": "INVALID_TOKEN_PAYLOAD",
                            "message": "Недействительный токен",
                            "details": {},
                        }
                    },
                )

            # Verify user still exists and is active
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user or not user.is_active:
                logger.warning(
                    "Token refresh for inactive/missing user", user_id=user_id
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": {
                            "code": "USER_INACTIVE",
                            "message": "Пользователь не активен",
                            "details": {},
                        }
                    },
                )

            # Create new access token
            new_access_token = jwt_service.create_access_token(user_id)

            logger.info("Access token refreshed", user_id=user_id)

            return RefreshResponse(access_token=new_access_token)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Token refresh error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "TOKEN_REFRESH_ERROR",
                        "message": "Ошибка при обновлении токена",
                        "details": {},
                    }
                },
            )

    async def logout(self, db: AsyncSession, access_token: str) -> dict:
        """
        Log out the user by blacklisting the current token.
        """
        try:
            # Blacklist the access token
            success = await jwt_service.blacklist_token(access_token)

            if success:
                logger.info("User logged out successfully")
                return {"message": "Успешный выход из системы"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": {
                            "code": "LOGOUT_ERROR",
                            "message": "Ошибка при выходе из системы",
                            "details": {},
                        }
                    },
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Logout error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "LOGOUT_ERROR",
                        "message": "Ошибка при выходе из системы",
                        "details": {},
                    }
                },
            )
