"""
Structured logging configuration using structlog.
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.processors import CallsiteParameterAdder

from app.core.config import get_settings


def configure_logging() -> None:
    """
    Configure structured logging for the application.
    """
    settings = get_settings()

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    # Configure structlog
    shared_processors = [
        # Add callsite information (file, line, function)
        CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ]
        ),
        # Add timestamp
        structlog.processors.TimeStamper(fmt="iso"),
        # Add log level
        structlog.stdlib.add_log_level,
        # Add logger name
        structlog.stdlib.add_logger_name,
        # Filter out private keys and sensitive information
        filter_sensitive_data,
        # Stack info processor for exceptions
        structlog.processors.StackInfoRenderer(),
        # Format exceptions
        structlog.dev.set_exc_info,
    ]

    if settings.is_development:
        # Development: pretty console output
        processors = shared_processors + [structlog.dev.ConsoleRenderer(colors=True)]
    else:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def filter_sensitive_data(
    logger: Any, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Filter out sensitive data from log entries.
    """
    sensitive_keys = {
        "password",
        "token",
        "api_key",
        "secret",
        "authorization",
        "jwt",
        "refresh_token",
        "access_token",
        "session_id",
        "verification_code",
    }

    def _filter_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively filter sensitive data from dictionaries."""
        filtered = {}
        for key, value in data.items():
            if isinstance(key, str) and any(
                sensitive in key.lower() for sensitive in sensitive_keys
            ):
                filtered[key] = "***REDACTED***"
            elif isinstance(value, dict):
                filtered[key] = _filter_dict(value)
            elif isinstance(value, list):
                filtered[key] = [
                    _filter_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
        return filtered

    return _filter_dict(event_dict)


class StructuredLogger:
    """
    Wrapper for structlog with additional convenience methods.
    """

    def __init__(self, name: Optional[str] = None):
        self.logger = structlog.get_logger(name)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self.logger.exception(message, **kwargs)

    def audit(self, action: str, user_id: Optional[str] = None, **kwargs: Any) -> None:
        """Log audit trail."""
        self.logger.info(
            "Audit log", action=action, user_id=user_id, log_type="audit", **kwargs
        )

    def performance(self, operation: str, duration: float, **kwargs: Any) -> None:
        """Log performance metrics."""
        self.logger.info(
            "Performance log",
            operation=operation,
            duration_ms=duration * 1000,
            log_type="performance",
            **kwargs,
        )

    def security(self, event: str, **kwargs: Any) -> None:
        """Log security events."""
        self.logger.warning(
            "Security event", event=event, log_type="security", **kwargs
        )

    def business(self, event: str, **kwargs: Any) -> None:
        """Log business events."""
        self.logger.info("Business event", event=event, log_type="business", **kwargs)


def get_logger(name: Optional[str] = None) -> StructuredLogger:
    """
    Get a structured logger instance.
    """
    return StructuredLogger(name)


# Pre-configured loggers for common use cases
api_logger = get_logger("api")
db_logger = get_logger("database")
auth_logger = get_logger("auth")
cache_logger = get_logger("cache")
sms_logger = get_logger("sms")
file_logger = get_logger("file")
business_logger = get_logger("business")

# Alias for backward compatibility
setup_logging = configure_logging
