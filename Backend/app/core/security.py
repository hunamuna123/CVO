"""
Comprehensive security module for authentication, authorization, and protection.

This module provides enterprise-grade security features including
JWT handling, role-based access control, rate limiting, and security headers.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from functools import wraps
import re

import bcrypt
import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import structlog

from app.core.config import get_settings
from app.models.user import User, UserRole
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidTokenError,
    TokenExpiredError,
    RateLimitExceededError,
)

logger = structlog.get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

# Settings
settings = get_settings()


class PasswordValidator:
    """Password validation with security rules."""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @staticmethod
    def validate_password(password: str) -> List[str]:
        """Validate password and return list of errors."""
        errors = []
        
        if len(password) < PasswordValidator.MIN_LENGTH:
            errors.append(f"Password must be at least {PasswordValidator.MIN_LENGTH} characters long")
        
        if len(password) > PasswordValidator.MAX_LENGTH:
            errors.append(f"Password must be at most {PasswordValidator.MAX_LENGTH} characters long")
        
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
        
        return errors
    
    @staticmethod
    def is_password_strong(password: str) -> bool:
        """Check if password meets all requirements."""
        return len(PasswordValidator.validate_password(password)) == 0


class PasswordManager:
    """Password hashing and verification."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a secure random password."""
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Ensure all requirements are met
        if not PasswordValidator.is_password_strong(password):
            return PasswordManager.generate_secure_password(length)
        
        return password


class TokenManager:
    """JWT token management."""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.refresh_token_expire_days
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                raise InvalidTokenError("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.JWTError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def extract_user_id(token: str) -> str:
        """Extract user ID from token."""
        payload = TokenManager.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise InvalidTokenError("Token does not contain user ID")
        
        return user_id


class RoleBasedAccessControl:
    """Role-based access control (RBAC) system."""
    
    # Define role hierarchy (higher number = higher privilege)
    ROLE_HIERARCHY = {
        UserRole.USER: 1,
        UserRole.DEVELOPER: 2,
        UserRole.ADMIN: 3,
    }
    
    # Define permissions for each role
    ROLE_PERMISSIONS = {
        UserRole.USER: [
            "profile:read",
            "profile:update",
            "properties:read",
            "favorites:create",
            "favorites:read",
            "favorites:delete",
            "reviews:create",
            "reviews:read",
            "leads:create",
        ],
        UserRole.DEVELOPER: [
            # All user permissions plus:
            "properties:create",
            "properties:update",
            "properties:delete",
            "developer:read",
            "developer:update",
            "leads:read",
            "analytics:read",
        ],
        UserRole.ADMIN: [
            # All permissions
            "*"
        ]
    }
    
    @classmethod
    def has_permission(cls, user_role: UserRole, permission: str) -> bool:
        """Check if user role has specific permission."""
        role_permissions = cls.ROLE_PERMISSIONS.get(user_role, [])
        
        # Admin has all permissions
        if "*" in role_permissions:
            return True
        
        # Check direct permission
        if permission in role_permissions:
            return True
        
        # Check wildcard permissions
        permission_parts = permission.split(":")
        if len(permission_parts) == 2:
            wildcard = f"{permission_parts[0]}:*"
            if wildcard in role_permissions:
                return True
        
        return False
    
    @classmethod
    def is_role_higher_or_equal(cls, user_role: UserRole, required_role: UserRole) -> bool:
        """Check if user role is higher or equal to required role."""
        user_level = cls.ROLE_HIERARCHY.get(user_role, 0)
        required_level = cls.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level


class SecurityHeaders:
    """Security headers for HTTP responses."""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get standard security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }


class IPAddressValidator:
    """IP address validation and filtering."""
    
    @staticmethod
    def is_private_ip(ip: str) -> bool:
        """Check if IP address is private."""
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except ValueError:
            return False
    
    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """Check if IP address is valid."""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False


class SessionManager:
    """User session management."""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate secure session ID."""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_session_data(user: User) -> Dict[str, Any]:
        """Create session data for user."""
        return {
            "user_id": str(user.id),
            "username": user.phone,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "created_at": datetime.utcnow().isoformat(),
        }


# Decorators for authorization
def require_permission(permission: str):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from kwargs or args
            current_user = None
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                    break
            
            if not current_user:
                current_user = kwargs.get('current_user')
            
            if not current_user:
                raise AuthorizationError("Authentication required")
            
            if not RoleBasedAccessControl.has_permission(current_user.role, permission):
                raise AuthorizationError(f"Permission '{permission}' required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role: UserRole):
    """Decorator to require specific role or higher."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from kwargs or args
            current_user = None
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                    break
            
            if not current_user:
                current_user = kwargs.get('current_user')
            
            if not current_user:
                raise AuthorizationError("Authentication required")
            
            if not RoleBasedAccessControl.is_role_higher_or_equal(current_user.role, role):
                raise AuthorizationError(f"Role '{role.value}' or higher required")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_verified_user(func):
    """Decorator to require verified user."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract current user from kwargs or args
        current_user = None
        for arg in args:
            if isinstance(arg, User):
                current_user = arg
                break
        
        if not current_user:
            current_user = kwargs.get('current_user')
        
        if not current_user:
            raise AuthorizationError("Authentication required")
        
        if not current_user.is_verified:
            raise AuthorizationError("Verified account required")
        
        return await func(*args, **kwargs)
    return wrapper


# Utility functions
def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"


def generate_csrf_token() -> str:
    """Generate CSRF token."""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected_token: str) -> bool:
    """Verify CSRF token."""
    return secrets.compare_digest(token, expected_token)


# Export main classes and functions
__all__ = [
    "PasswordValidator",
    "PasswordManager", 
    "TokenManager",
    "RoleBasedAccessControl",
    "SecurityHeaders",
    "IPAddressValidator",
    "SessionManager",
    "require_permission",
    "require_role",
    "require_verified_user",
    "get_client_ip",
    "generate_csrf_token",
    "verify_csrf_token",
]
