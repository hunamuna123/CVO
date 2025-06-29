"""
JWT token service for authentication and authorization.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import structlog
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis
from app.models.user import User, UserRole

logger = structlog.get_logger(__name__)
settings = get_settings()


class JWTService:
    """
    Service for JWT token operations.
    """

    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def create_access_token(
        self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create access token for user.
        """
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": user_id,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        if additional_claims:
            payload.update(additional_claims)

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info("Access token created", user_id=user_id, expires_at=expire)

        return token

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create refresh token for user.
        """
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)

        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info("Refresh token created", user_id=user_id, expires_at=expire)

        return token

    def verify_token(
        self, token: str, token_type: str = "access"
    ) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != token_type:
                logger.warning(
                    "Invalid token type", expected=token_type, got=payload.get("type")
                )
                return None

            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token expired", user_id=payload.get("sub"))
                return None

            return payload

        except JWTError as e:
            logger.warning("JWT decode error", error=str(e))
            return None

    async def get_user_from_token(self, db: AsyncSession, token: str) -> Optional[User]:
        """
        Get user from access token.
        """
        payload = self.verify_token(token, "access")
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Check if token is blacklisted
        redis = await get_redis()
        is_blacklisted = await redis.get(f"blacklist:{token}")
        if is_blacklisted:
            logger.warning("Token is blacklisted", user_id=user_id)
            return None

        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            logger.warning("User not found or inactive", user_id=user_id)
            return None

        return user

    async def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist.
        """
        try:
            payload = self.verify_token(token)
            if not payload:
                return False

            # Calculate remaining TTL
            exp = payload.get("exp")
            if exp:
                ttl = max(0, int(exp - datetime.utcnow().timestamp()))

                redis = await get_redis()
                await redis.setex(f"blacklist:{token}", ttl, "1")

                logger.info("Token blacklisted", user_id=payload.get("sub"), ttl=ttl)
                return True

            return False

        except Exception as e:
            logger.error("Error blacklisting token: %s", str(e))
            return False

    def create_token_pair(self, user_id: str) -> Dict[str, str]:
        """
        Create both access and refresh tokens.
        """
        access_token = self.create_access_token(user_id)
        refresh_token = self.create_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }


# Global JWT service instance
jwt_service = JWTService()
