"""
Custom exceptions and error handling.
"""

from typing import Any, Dict, Optional, Union

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = structlog.get_logger(__name__)


class BaseAPIException(Exception):
    """
    Base exception class for API errors.
    """

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication and Authorization Exceptions
class AuthenticationError(BaseAPIException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_FAILED",
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials provided."""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message)
        self.error_code = "INVALID_CREDENTIALS"


class TokenExpiredError(AuthenticationError):
    """JWT token has expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message=message)
        self.error_code = "TOKEN_EXPIRED"


class InvalidTokenError(AuthenticationError):
    """Invalid JWT token."""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message=message)
        self.error_code = "INVALID_TOKEN"


class AuthorizationError(BaseAPIException):
    """Authorization failed."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="ACCESS_DENIED",
        )


class InsufficientPermissionsError(AuthorizationError):
    """User doesn't have required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message=message)
        self.error_code = "INSUFFICIENT_PERMISSIONS"


# Validation Exceptions
class ValidationError(BaseAPIException):
    """Data validation failed."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class InvalidPhoneNumberError(ValidationError):
    """Invalid phone number format."""

    def __init__(self, phone: str):
        super().__init__(
            message="Invalid phone number format",
            details={"phone": phone},
        )
        self.error_code = "INVALID_PHONE_NUMBER"


class InvalidEmailError(ValidationError):
    """Invalid email format."""

    def __init__(self, email: str):
        super().__init__(
            message="Invalid email format",
            details={"email": email},
        )
        self.error_code = "INVALID_EMAIL"


# Resource Exceptions
class NotFoundError(BaseAPIException):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"

        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id},
        )


class ConflictError(BaseAPIException):
    """Resource conflict."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT",
        )


class AlreadyExistsError(ConflictError):
    """Resource already exists."""

    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            message=f"{resource} with {field} '{value}' already exists",
        )
        self.error_code = "RESOURCE_ALREADY_EXISTS"
        self.details = {"resource": resource, "field": field, "value": value}


# Business Logic Exceptions
class BusinessLogicError(BaseAPIException):
    """Business logic violation."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_LOGIC_ERROR",
        )


class InvalidPropertyStatusError(BusinessLogicError):
    """Invalid property status transition."""

    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            message=f"Cannot change status from {current_status} to {new_status}",
        )
        self.error_code = "INVALID_STATUS_TRANSITION"
        self.details = {"current_status": current_status, "new_status": new_status}


class PropertyNotAvailableError(BusinessLogicError):
    """Property is not available for the requested operation."""

    def __init__(self, property_id: str, operation: str):
        super().__init__(
            message=f"Property {property_id} is not available for {operation}",
        )
        self.error_code = "PROPERTY_NOT_AVAILABLE"
        self.details = {"property_id": property_id, "operation": operation}


# File Upload Exceptions
class FileUploadError(BaseAPIException):
    """File upload error."""

    def __init__(self, message: str = "File upload failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="FILE_UPLOAD_ERROR",
        )


class FileSizeExceededError(FileUploadError):
    """File size exceeds limit."""

    def __init__(self, max_size: int, actual_size: int):
        super().__init__(
            message=f"File size {actual_size} bytes exceeds limit of {max_size} bytes",
        )
        self.error_code = "FILE_SIZE_EXCEEDED"
        self.details = {"max_size": max_size, "actual_size": actual_size}


class InvalidFileTypeError(FileUploadError):
    """Invalid file type."""

    def __init__(self, file_type: str, allowed_types: list):
        super().__init__(
            message=f"File type '{file_type}' not allowed. Allowed types: {', '.join(allowed_types)}",
        )
        self.error_code = "INVALID_FILE_TYPE"
        self.details = {"file_type": file_type, "allowed_types": allowed_types}


# Rate Limiting Exceptions
class RateLimitExceededError(BaseAPIException):
    """Rate limit exceeded."""

    def __init__(self, limit: str, retry_after: Optional[int] = None):
        super().__init__(
            message=f"Rate limit exceeded: {limit}",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )
        if retry_after:
            self.details = {"retry_after": retry_after}


# SMS Service Exceptions
class SMSServiceError(BaseAPIException):
    """SMS service error."""

    def __init__(self, message: str = "SMS service error"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="SMS_SERVICE_ERROR",
        )


class InvalidVerificationCodeError(BaseAPIException):
    """Invalid verification code."""

    def __init__(self, message: str = "Invalid verification code"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_VERIFICATION_CODE",
        )


class VerificationCodeExpiredError(BaseAPIException):
    """Verification code has expired."""

    def __init__(self, message: str = "Verification code has expired"):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VERIFICATION_CODE_EXPIRED",
        )


# Aliases for backward compatibility and common naming patterns
NotFoundException = NotFoundError
ConflictException = ConflictError
BadRequestException = BusinessLogicError


# Exception Handlers
async def global_exception_handler(
    request: Request, exc: BaseAPIException
) -> JSONResponse:
    """
    Global exception handler for custom API exceptions.
    """
    logger.error(
        "API exception occurred",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        url=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    """
    # Format validation errors
    errors = {}
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        if field_path in errors:
            if isinstance(errors[field_path], list):
                errors[field_path].append(error["msg"])
            else:
                errors[field_path] = [errors[field_path], error["msg"]]
        else:
            errors[field_path] = error["msg"]

    logger.warning(
        "Validation error occurred",
        errors=errors,
        url=str(request.url),
        method=request.method,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Data validation failed",
                "details": errors,
            }
        },
    )


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create a standardized error response.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {},
            }
        },
    )
