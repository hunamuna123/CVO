"""
Main FastAPI application entry point.
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import create_db_connection, close_db_connection
from app.core.exceptions import (
    BaseAPIException,
    global_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging
from app.core.redis import close_redis_connection, create_redis_connection
from app.core.mongodb import create_mongodb_connection, close_mongodb_connection
from app.core.clickhouse import create_clickhouse_connection, close_clickhouse_connection
from app.core.kafka import create_kafka_connection, close_kafka_connection
from app.core.monitoring import (
    PrometheusMiddleware,
    setup_metrics,
    get_metrics,
    HealthChecker,
)

# Configure structured logging
setup_logging()
logger = structlog.get_logger(__name__)

# Get application settings
settings = get_settings()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up the application", app_name=settings.app_name)

    try:
        # Initialize core services
        await create_db_connection()
        logger.info("Database connection established")
        
        # Configure dependency injection services
        from app.core.dependencies import ensure_services_configured
        ensure_services_configured()
        logger.info("Service dependencies configured")

        try:
            await create_redis_connection()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
        
        # Initialize optional services (with error handling)
        try:
            await create_mongodb_connection()
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.warning(f"MongoDB connection failed: {e}")
        
        try:
            await create_clickhouse_connection()
            logger.info("ClickHouse connection established")
        except Exception as e:
            logger.warning(f"ClickHouse connection failed: {e}")
        
        try:
            await create_kafka_connection()
            logger.info("Kafka connection established")
        except Exception as e:
            logger.warning(f"Kafka connection failed: {e}")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down the application")

    try:
        await close_kafka_connection()
        logger.info("Kafka connection closed")
    except Exception:
        pass
    
    try:
        await close_clickhouse_connection()
        logger.info("ClickHouse connection closed")
    except Exception:
        pass
        
    try:
        await close_mongodb_connection()
        logger.info("MongoDB connection closed")
    except Exception:
        pass

    await close_redis_connection()
    logger.info("Redis connection closed")

    await close_db_connection()
    logger.info("Database connection closed")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """
    app = FastAPI(
        title="🏠 Real Estate Platform API",
        version=settings.version,
        description="""
        TODO: docs
        """,
        contact={
            "name": "Real Estate API Team",
            "url": "https://github.com/yourproject/realestate-api",
            "email": "api@realestate.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        terms_of_service="https://realestate-api.com/terms",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "list",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "syntaxHighlight.theme": "nord",
        },
        lifespan=lifespan,
    )

    # Add middlewares
    setup_middlewares(app)

    # Add exception handlers
    setup_exception_handlers(app)

    # Include routers
    app.include_router(api_router, prefix="/api/v1")

    # Mount static files for media
    import os

    media_path = settings.media_root
    if not os.path.exists(media_path):
        os.makedirs(media_path, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_path), name="media")

    # Add comprehensive health check endpoint
    @app.get("/health")
    async def health_check():
        """Comprehensive health check endpoint."""
        return await HealthChecker.get_overall_health()

    # Add Prometheus metrics endpoint
    @app.get("/metrics", response_class=PlainTextResponse)
    async def prometheus_metrics():
        """Prometheus metrics endpoint."""
        return get_metrics()
    
    # Add basic health endpoint for load balancers
    @app.get("/ping")
    async def ping():
        """Simple ping endpoint for load balancers."""
        return {"status": "ok", "timestamp": time.time()}

    return app


def setup_middlewares(app: FastAPI) -> None:
    """
    Configure application middlewares.
    """
    # CORS middleware
    settings = get_settings()
    allowed_origins = (
        settings.allowed_origins.split(",")
        if settings.allowed_origins != "*"
        else ["*"]
    )
    allowed_methods = settings.allowed_methods.split(",")
    allowed_headers = (
        settings.allowed_headers.split(",")
        if settings.allowed_headers != "*"
        else ["*"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        allow_credentials=True,
    )

    # Gzip compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Rate limiting middleware
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next) -> Response:
        """Log all incoming requests."""
        start_time = time.time()

        # Get client IP
        client_ip = get_remote_address(request)

        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent"),
        )

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time=process_time,
            client_ip=client_ip,
        )

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configure global exception handlers.
    """
    # Rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Custom API exception handler
    app.add_exception_handler(BaseAPIException, global_exception_handler)

    # Validation exception handler
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # General exception handler
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(
            "Unexpected error occurred",
            error=str(exc),
            url=str(request.url),
            method=request.method,
            exc_info=True,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {} if not settings.debug else {"error": str(exc)},
                }
            },
        )


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
