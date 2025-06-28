"""
SMS service for sending verification codes.
"""

import random
import string
from datetime import timedelta
from typing import Optional

import httpx
import structlog
from fastapi import HTTPException

from app.core.config import get_settings
from app.core.redis import get_redis

logger = structlog.get_logger(__name__)
settings = get_settings()


class SMSService:
    """
    Service for SMS operations and verification codes.
    """

    def __init__(self):
        self.api_key = settings.sms_api_key
        self.sender = settings.sms_sender
        self.provider = settings.sms_provider
        self.code_length = 4
        self.code_ttl = 300  # 5 minutes
        self.max_attempts = 3
        self.rate_limit_ttl = 3600  # 1 hour

    def generate_verification_code(self) -> str:
        """
        Generate 4-digit verification code.
        """
        return "".join(random.choices(string.digits, k=self.code_length))

    async def send_verification_code(self, phone: str, session_id: str) -> bool:
        """
        Send verification code via SMS.
        """
        try:
            # Check rate limiting
            redis = await get_redis()
            rate_limit_key = f"sms_rate_limit:{phone}"
            attempts = await redis.get(rate_limit_key)

            if attempts and int(attempts) >= self.max_attempts:
                logger.warning(
                    "SMS rate limit exceeded", phone=phone, attempts=attempts
                )
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": "Превышен лимит отправки SMS. Попробуйте через час.",
                            "details": {"retry_after": "1 hour"},
                        }
                    },
                )

            # Generate verification code
            code = self.generate_verification_code()

            # Store code in Redis
            code_key = f"verification_code:{session_id}"
            await redis.setex(code_key, self.code_ttl, code)

            # Store phone for this session
            phone_key = f"verification_phone:{session_id}"
            await redis.setex(phone_key, self.code_ttl, phone)

            # Send SMS
            success = await self._send_sms(phone, code)

            if success:
                # Increment rate limit counter
                current_attempts = await redis.incr(rate_limit_key)
                if current_attempts == 1:
                    await redis.expire(rate_limit_key, self.rate_limit_ttl)

                logger.info("Verification SMS sent", phone=phone, session_id=session_id)
                return True
            else:
                # Remove stored code if SMS failed
                await redis.delete(code_key, phone_key)
                logger.error("Failed to send SMS", phone=phone)
                return False

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error sending verification SMS", phone=phone, error=str(e))
            return False

    async def verify_code(self, session_id: str, code: str) -> Optional[str]:
        """
        Verify SMS code and return phone number if valid.
        """
        try:
            redis = await get_redis()

            # Get stored code and phone
            code_key = f"verification_code:{session_id}"
            phone_key = f"verification_phone:{session_id}"

            stored_code = await redis.get(code_key)
            stored_phone = await redis.get(phone_key)

            if not stored_code or not stored_phone:
                logger.warning("Verification session not found", session_id=session_id)
                return None

            # Verify code - handle both bytes and string responses from Redis
            stored_code_str = (
                stored_code.decode() if isinstance(stored_code, bytes) else stored_code
            )
            if stored_code_str != code:
                logger.warning("Invalid verification code", session_id=session_id)
                return None

            # Code is valid, cleanup
            await redis.delete(code_key, phone_key)

            phone = (
                stored_phone.decode()
                if isinstance(stored_phone, bytes)
                else stored_phone
            )
            logger.info(
                "Verification code verified", phone=phone, session_id=session_id
            )

            return phone

        except Exception as e:
            logger.error(
                "Error verifying SMS code", session_id=session_id, error=str(e)
            )
            return None

    async def _send_sms(self, phone: str, code: str) -> bool:
        """
        Send SMS using configured provider.
        """
        if settings.environment == "development":
            # In development, just log the code
            logger.info("SMS CODE (DEV MODE)", phone=phone, code=code)
            return True

        try:
            if self.provider == "sms_ru":
                return await self._send_sms_ru(phone, code)
            else:
                logger.error("Unknown SMS provider", provider=self.provider)
                return False

        except Exception as e:
            logger.error("SMS provider error", provider=self.provider, error=str(e))
            return False

    async def _send_sms_ru(self, phone: str, code: str) -> bool:
        """
        Send SMS using SMS.RU API.
        """
        url = "https://sms.ru/sms/send"

        message = f"Ваш код подтверждения: {code}. Не сообщайте его никому."

        params = {
            "api_id": self.api_key,
            "to": phone,
            "msg": message,
            "from": self.sender,
            "json": 1,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=params, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK":
                    logger.info("SMS sent successfully via SMS.RU", phone=phone)
                    return True
                else:
                    logger.error("SMS.RU error", phone=phone, response=data)
                    return False
            else:
                logger.error(
                    "SMS.RU HTTP error", phone=phone, status=response.status_code
                )
                return False

    async def cleanup_expired_codes(self):
        """
        Cleanup expired verification codes (can be called by background task).
        """
        try:
            redis = await get_redis()

            # Redis automatically expires keys, but we can add additional cleanup if needed
            logger.debug("SMS cleanup completed")

        except Exception as e:
            logger.error("Error during SMS cleanup", error=str(e))


# Global SMS service instance
sms_service = SMSService()
