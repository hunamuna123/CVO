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
# 🏠 Платформа недвижимости - API документация

## 📋 Описание

**Real Estate Platform API** - это мощная и современная REST API платформа для управления недвижимостью, 
разработанная с использованием FastAPI, PostgreSQL, Redis, MongoDB, ClickHouse и Apache Kafka.

### ✨ Основные возможности

- 🔐 **Аутентификация и авторизация** - JWT токены, роли пользователей
- 🏢 **Управление застройщиками** - верификация, профили, рейтинги
- 🏘️ **Управление недвижимостью** - создание, редактирование, поиск объектов
- 🏗️ **Жилые комплексы** - управление ЖК, планировки, инфраструктура
- 📊 **Аналитика и отчеты** - статистика, метрики, прогнозы
- 💰 **Динамическое ценообразование** - автоматическая корректировка цен
- 📝 **Система бронирования** - резервирование объектов, платежи
- 🎯 **Избранное и история** - персонализация для пользователей
- 📱 **Отзывы и рейтинги** - система отзывов о застройщиках
- 🤖 **ИИ-рекомендации** - умные алгоритмы подбора недвижимости
- 📈 **Система лидов** - управление потенциальными клиентами
- 🎫 **Промокоды** - скидки и специальные предложения

### 🏗️ Архитектура

#### 🛢️ Базы данных
- **PostgreSQL** - основные данные (пользователи, недвижимость, застройщики)
- **Redis** - кэширование, сессии, очереди задач
- **MongoDB** - документы, файлы, неструктурированные данные
- **ClickHouse** - аналитика, метрики, агрегация данных

#### 🔄 Интеграции
- **Apache Kafka** - обработка событий в реальном времени
- **File Storage** - S3-совместимое хранилище файлов
- **SMS Gateway** - отправка SMS для верификации
- **Email Service** - уведомления и рассылки

### 🚀 Технологический стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM для работы с БД
- **Alembic** - миграции базы данных  
- **Pydantic** - валидация данных
- **AsyncIO** - асинхронное программирование
- **Structlog** - структурированное логирование
- **Prometheus** - мониторинг и метрики
- **Docker** - контейнеризация

### 📚 Структура API

#### 👤 Пользователи (`/users`)
- Регистрация и управление профилями
- Роли: USER, DEVELOPER, ADMIN
- Верификация по телефону

#### 🔐 Аутентификация (`/auth`)
- JWT access/refresh токены
- SMS-верификация
- Сброс пароля

#### 🏢 Застройщики (`/developers`)
- Профили компаний
- Верификация документов
- Рейтинги и отзывы

#### 🏠 Недвижимость (`/properties`)
- CRUD операции
- Продвинутый поиск и фильтрация
- Загрузка изображений и документов
- Геолокация

#### 🏗️ Жилые комплексы (`/complexes`)
- Управление ЖК
- Планировки и схемы
- Инфраструктура

#### 📊 Аналитика (`/analytics`)
- Статистика просмотров
- Отчеты по продажам
- Рыночная аналитика

#### 📝 Бронирование (`/bookings`)
- Резервирование объектов
- Статусы бронирований
- Интеграция с платежами

#### ⭐ Избранное (`/favorites`)
- Добавление в избранное
- Персональные коллекции

#### 📝 Отзывы (`/reviews`)
- Отзывы о застройщиках
- Модерация контента

#### 🎯 Лиды (`/leads`)
- Заявки клиентов
- CRM функционал

#### 🎫 Промокоды (`/promo-codes`)
- Создание акций
- Система скидок

#### 🤖 ИИ-сервисы (`/ai`)
- Рекомендации недвижимости
- Чат-бот консультант
- Анализ рынка
- Прогнозирование цен

### 🔒 Безопасность

- **JWT Authentication** - безопасная аутентификация
- **Role-based Access Control** - ролевая модель доступа
- **Rate Limiting** - защита от злоупотреблений
- **Input Validation** - валидация всех входных данных
- **CORS Protection** - настройка междоменных запросов
- **SQL Injection Protection** - защита от SQL-инъекций

### 📝 Примеры использования

#### Поиск недвижимости
```http
GET /api/v1/properties?city=Москва&property_type=APARTMENT&price_min=5000000&rooms_count=2,3
```

#### Создание объекта недвижимости
```http
POST /api/v1/properties
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "3-комнатная квартира в центре",
  "price": 15000000,
  "property_type": "APARTMENT",
  "deal_type": "SALE",
  "city": "Москва",
  "rooms_count": 3
}
```

### 🚦 Коды ответов

- **200** - Успешный запрос
- **201** - Ресурс создан
- **400** - Ошибка валидации данных
- **401** - Не авторизован
- **403** - Доступ запрещен
- **404** - Ресурс не найден
- **429** - Превышен лимит запросов
- **500** - Внутренняя ошибка сервера
        """,
        contact={
            "name": "Кириешки",
            "url": "https://github.com/hunamuna123/CVO",
            "email": "has_to@be.set",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        terms_of_service="https://realestate-api.com/terms",
        tags_metadata=[
            {
                "name": "Authentication",
                "description": "🔐 **Аутентификация и авторизация**\n\n" +
                              "Управление пользователями, JWT токены, SMS-верификация, сброс паролей.\n\n" +
                              "- Регистрация и авторизация\n" +
                              "- JWT access/refresh токены\n" +
                              "- SMS код подтверждения\n" +
                              "- Восстановление доступа",
                "externalDocs": {
                    "description": "Документация по безопасности",
                    "url": "https://realestate-api.com/docs/auth",
                },
            },
            {
                "name": "Users",
                "description": "👤 **Управление пользователями**\n\n" +
                              "Профили пользователей, роли, настройки аккаунта.\n\n" +
                              "- Создание и редактирование профилей\n" +
                              "- Управление ролями (USER, DEVELOPER, ADMIN)\n" +
                              "- Настройки приватности\n" +
                              "- История активности",
            },
            {
                "name": "Developers",
                "description": "🏢 **Управление застройщиками**\n\n" +
                              "Профили компаний-застройщиков, верификация, рейтинги.\n\n" +
                              "- Регистрация компаний\n" +
                              "- Верификация документов\n" +
                              "- Управление рейтингами\n" +
                              "- Портфолио проектов",
            },
            {
                "name": "Properties",
                "description": "🏠 **Управление недвижимостью**\n\n" +
                              "Создание, редактирование и поиск объектов недвижимости.\n\n" +
                              "- CRUD операции с объектами\n" +
                              "- Продвинутый поиск и фильтрация\n" +
                              "- Загрузка изображений и документов\n" +
                              "- Геолокация и карты\n" +
                              "- Управление статусами",
            },
            {
                "name": "Complexes",
                "description": "🏗️ **Жилые комплексы**\n\n" +
                              "Управление жилыми комплексами и их инфраструктурой.\n\n" +
                              "- Создание и управление ЖК\n" +
                              "- Планировки и схемы\n" +
                              "- Инфраструктура и удобства\n" +
                              "- Этапы строительства",
            },
            {
                "name": "Analytics",
                "description": "📊 **Аналитика и отчеты**\n\n" +
                              "Статистика, метрики и аналитические отчеты.\n\n" +
                              "- Статистика просмотров и активности\n" +
                              "- Отчеты по продажам\n" +
                              "- Рыночная аналитика\n" +
                              "- Прогнозирование трендов",
            },
            {
                "name": "Bookings",
                "description": "📝 **Система бронирования**\n\n" +
                              "Резервирование объектов недвижимости и управление сделками.\n\n" +
                              "- Создание бронирований\n" +
                              "- Статусы и жизненный цикл\n" +
                              "- Интеграция с платежами\n" +
                              "- Управление комиссиями",
            },
            {
                "name": "Favorites",
                "description": "⭐ **Избранное**\n\n" +
                              "Персональные коллекции пользователей.\n\n" +
                              "- Добавление в избранное\n" +
                              "- Персональные списки\n" +
                              "- Уведомления об изменениях",
            },
            {
                "name": "Reviews",
                "description": "📝 **Отзывы и рейтинги**\n\n" +
                              "Система отзывов о застройщиках и объектах.\n\n" +
                              "- Создание отзывов\n" +
                              "- Система рейтингов\n" +
                              "- Модерация контента\n" +
                              "- Анализ репутации",
            },
            {
                "name": "Leads",
                "description": "🎯 **Система лидов**\n\n" +
                              "Управление потенциальными клиентами и заявками.\n\n" +
                              "- Создание лидов\n" +
                              "- CRM функционал\n" +
                              "- Воронка продаж\n" +
                              "- Конверсионная аналитика",
            },
            {
                "name": "Promo Codes",
                "description": "🎫 **Промокоды и акции**\n\n" +
                              "Система скидок и специальных предложений.\n\n" +
                              "- Создание промокодов\n" +
                              "- Гибкие условия использования\n" +
                              "- Геотаргетинг\n" +
                              "- Аналитика эффективности",
            },
            {
                "name": "AI Services",
                "description": "🤖 **ИИ-сервисы**\n\n" +
                              "Искусственный интеллект для анализа и рекомендаций.\n\n" +
                              "- Персональные рекомендации\n" +
                              "- Чат-бот консультант\n" +
                              "- Анализ рынка и трендов\n" +
                              "- Прогнозирование цен\n" +
                              "- Инвестиционные возможности",
            },
        ],
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
        allow_origins=["*"],  # Allow all origins for development
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        allow_headers=["*"],  # Allow all headers
        allow_credentials=True,
        expose_headers=["*"],
        max_age=600,  # Cache preflight for 10 minutes (shorter for debugging)
    )

    # Gzip compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Rate limiting middleware
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # Explicit CORS headers middleware for zrok compatibility
    @app.middleware("http")
    async def add_cors_headers(request: Request, call_next) -> Response:
        """Add explicit CORS headers to all responses."""
        origin = request.headers.get("origin", "unknown")
        
        # Log CORS requests for debugging
        if request.method == "OPTIONS" or origin != "unknown":
            logger.info(
                "CORS request detected",
                method=request.method,
                origin=origin,
                url=str(request.url),
                user_agent=request.headers.get("user-agent", "unknown")
            )
        
        # Handle preflight requests immediately
        if request.method == "OPTIONS":
            cors_headers = {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
                "Access-Control-Expose-Headers": "*",
                "Vary": "Origin",
                "Content-Type": "application/json",
            }
            
            logger.info(
                "OPTIONS preflight response",
                origin=origin,
                headers=list(cors_headers.keys())
            )
            
            return JSONResponse(
                content={"message": "OK", "method": "OPTIONS", "origin": origin},
                headers=cors_headers
            )
        
        response = await call_next(request)
        
        # Add CORS headers to all responses
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Expose-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.headers["Vary"] = "Origin"
        
        # Additional headers for better compatibility
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        
        # Log successful CORS response
        if origin != "unknown":
            logger.info(
                "CORS response sent",
                method=request.method,
                origin=origin,
                status_code=response.status_code
            )
        
        return response

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
