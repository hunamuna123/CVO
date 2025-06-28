# Техническое задание: Backend API для платформы недвижимости

## 1. Общие требования

### 1.1 Архитектура

- **REST API** с использованием FastAPI (Python 3.13+)
- **PostgreSQL 15+** в качестве основной БД
- **Redis 7+** для кэширования и сессий
- **JWT** токены для аутентификации
- **Swagger/OpenAPI** документация
- **Docker** контейнеризация

### 1.2 Принципы разработки

- Все endpoint'ы должны возвращать JSON
- Пагинация для всех списочных endpoint'ов
- Валидация данных с помощью Pydantic
- Логирование всех операций
- Обработка ошибок с понятными сообщениями

---

## 2. Модели данных

### 2.1 User (Пользователь)

```python
{
    "id": "UUID",
    "phone": "string",  # Обязательный, уникальный, для регистрации
    "email": "string|null",  # Опциональный
    "first_name": "string",  # Имя, обязательный
    "last_name": "string",   # Фамилия, обязательный
    "middle_name": "string|null",  # Отчество, опциональный
    "role": "enum",  # USER, DEVELOPER, ADMIN
    "is_active": "boolean",
    "is_verified": "boolean",  # Подтвержден ли телефон
    "avatar_url": "string|null",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### 2.2 Developer (Застройщик)

```python
{
    "id": "UUID",
    "user_id": "UUID",  # FK к User
    "company_name": "string",  # Название компании
    "legal_name": "string",    # Юридическое название
    "inn": "string",           # ИНН, уникальный
    "ogrn": "string",          # ОГРН
    "legal_address": "string", # Юридический адрес
    "contact_phone": "string",
    "contact_email": "string",
    "website": "string|null",
    "description": "text|null",
    "logo_url": "string|null",
    "rating": "float",         # Средний рейтинг 0-5
    "reviews_count": "integer",
    "is_verified": "boolean",  # Прошел верификацию
    "verification_status": "enum",  # PENDING, APPROVED, REJECTED
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### 2.3 Property (Объект недвижимости)

```python
{
    "id": "UUID",
    "developer_id": "UUID",  # FK к Developer
    "title": "string",       # Название объекта
    "description": "text",
    "property_type": "enum", # APARTMENT, HOUSE, COMMERCIAL
    "deal_type": "enum",     # SALE, RENT
    "price": "decimal",      # Цена в рублях
    "price_per_sqm": "decimal|null",  # Цена за м²
    "currency": "string",    # RUB по умолчанию

    # Адрес
    "region": "string",
    "city": "string",
    "district": "string|null",
    "street": "string",
    "house_number": "string",
    "apartment_number": "string|null",
    "postal_code": "string|null",
    "latitude": "float|null",
    "longitude": "float|null",

    # Характеристики
    "total_area": "float|null",      # Общая площадь
    "living_area": "float|null",     # Жилая площадь
    "kitchen_area": "float|null",    # Площадь кухни
    "rooms_count": "integer|null",   # Количество комнат
    "bedrooms_count": "integer|null", # Количество спален
    "bathrooms_count": "integer|null", # Количество санузлов
    "floor": "integer|null",         # Этаж
    "total_floors": "integer|null",  # Всего этажей в доме
    "building_year": "integer|null", # Год постройки
    "ceiling_height": "float|null",  # Высота потолков

    # Особенности
    "has_balcony": "boolean",
    "has_loggia": "boolean",
    "has_elevator": "boolean",
    "has_parking": "boolean",
    "has_furniture": "boolean",
    "renovation_type": "enum|null",  # NONE, COSMETIC, EURO, DESIGNER

    # Статус
    "status": "enum",         # DRAFT, ACTIVE, SOLD, RENTED, ARCHIVED
    "is_featured": "boolean", # Рекламируемый объект
    "views_count": "integer",
    "favorites_count": "integer",

    # Временные поля
    "available_from": "date|null",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### 2.4 PropertyImage (Изображения объекта)

```python
{
    "id": "UUID",
    "property_id": "UUID",  # FK к Property
    "url": "string",        # URL изображения
    "title": "string|null", # Описание фото
    "is_main": "boolean",   # Главное фото
    "order": "integer",     # Порядок отображения
    "created_at": "datetime"
}
```

### 2.5 PropertyDocument (Документы объекта)

```python
{
    "id": "UUID",
    "property_id": "UUID",  # FK к Property
    "document_type": "enum", # PLAN, CERTIFICATE, CONTRACT, OTHER
    "title": "string",
    "file_url": "string",
    "file_size": "integer", # Размер в байтах
    "mime_type": "string",
    "is_verified": "boolean",
    "created_at": "datetime"
}
```

### 2.6 Favorite (Избранное)

```python
{
    "id": "UUID",
    "user_id": "UUID",      # FK к User
    "property_id": "UUID",  # FK к Property
    "created_at": "datetime"
}
```

### 2.7 Review (Отзывы)

```python
{
    "id": "UUID",
    "user_id": "UUID",      # FK к User
    "developer_id": "UUID", # FK к Developer
    "property_id": "UUID|null", # FK к Property (опционально)
    "rating": "integer",    # Оценка 1-5
    "title": "string",
    "content": "text",
    "is_verified": "boolean", # Проверен модератором
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

### 2.8 SearchHistory (История поиска)

```python
{
    "id": "UUID",
    "user_id": "UUID|null", # FK к User (может быть анонимный)
    "session_id": "string", # Для анонимных пользователей
    "search_query": "text", # Поисковый запрос
    "filters": "json",      # Примененные фильтры
    "results_count": "integer",
    "created_at": "datetime"
}
```

### 2.9 ViewHistory (История просмотров)

```python
{
    "id": "UUID",
    "user_id": "UUID|null", # FK к User
    "property_id": "UUID",  # FK к Property
    "session_id": "string",
    "ip_address": "string",
    "user_agent": "string|null",
    "created_at": "datetime"
}
```

### 2.10 Lead (Заявки)

```python
{
    "id": "UUID",
    "property_id": "UUID",  # FK к Property
    "user_id": "UUID|null", # FK к User (может быть анонимная заявка)
    "name": "string",
    "phone": "string",
    "email": "string|null",
    "message": "text|null",
    "lead_type": "enum",    # CALL_REQUEST, VIEWING, CONSULTATION
    "status": "enum",       # NEW, IN_PROGRESS, COMPLETED, CANCELLED
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

---

## 3. API Endpoints

### 3.1 Аутентификация

#### POST /api/auth/register

Регистрация нового пользователя по номеру телефона

```python
# Request
{
    "phone": "+79999999999",
    "first_name": "Иван",
    "last_name": "Петров",
    "middle_name": "Сергеевич",  # optional
    "email": "ivan@example.com"  # optional
}

# Response
{
    "message": "SMS с кодом отправлен",
    "session_id": "uuid"
}
```

#### POST /api/auth/verify

Подтверждение регистрации SMS-кодом

```python
# Request
{
    "session_id": "uuid",
    "verification_code": "1234"
}

# Response
{
    "access_token": "jwt_token",
    "refresh_token": "jwt_token",
    "user": {User object}
}
```

#### POST /api/auth/login

Вход по номеру телефона

```python
# Request
{
    "phone": "+79999999999"
}

# Response
{
    "message": "SMS с кодом отправлен",
    "session_id": "uuid"
}
```

#### POST /api/auth/refresh

Обновление access токена

```python
# Request
{
    "refresh_token": "jwt_token"
}

# Response
{
    "access_token": "jwt_token"
}
```

#### POST /api/auth/logout

Выход из системы

### 3.2 Пользователи

#### GET /api/users/me

Получение информации о текущем пользователе

#### PUT /api/users/me

Обновление профиля пользователя

#### POST /api/users/me/avatar

Загрузка аватара

### 3.3 Застройщики

#### GET /api/developers

Получение списка застройщиков с фильтрацией и пагинацией

```python
# Query параметры
{
    "page": 1,
    "limit": 20,
    "city": "Москва",
    "is_verified": true,
    "rating_min": 4.0
}
```

#### GET /api/developers/{developer_id}

Получение информации о застройщике

#### POST /api/developers (Требует аутентификации)

Создание профиля застройщика

#### PUT /api/developers/{developer_id} (Требует права)

Обновление профиля застройщика

### 3.4 Объекты недвижимости

#### GET /api/properties

Поиск объектов с фильтрацией и пагинацией

```python
# Query параметры
{
    "page": 1,
    "limit": 20,
    "city": "Москва",
    "property_type": "APARTMENT",
    "deal_type": "SALE",
    "price_min": 5000000,
    "price_max": 15000000,
    "rooms_count": [1, 2, 3],
    "total_area_min": 40,
    "has_parking": true,
    "sort": "price_asc"  # price_asc, price_desc, created_desc, area_asc
}
```

#### GET /api/properties/{property_id}

Получение детальной информации об объекте

#### POST /api/properties (Требует права застройщика)

Создание нового объекта

#### PUT /api/properties/{property_id} (Требует права)

Обновление объекта

#### DELETE /api/properties/{property_id} (Требует права)

Удаление объекта

#### POST /api/properties/{property_id}/images

Загрузка изображений объекта

#### DELETE /api/properties/{property_id}/images/{image_id}

Удаление изображения

#### POST /api/properties/{property_id}/documents

Загрузка документов объекта

### 3.5 Избранное

#### GET /api/favorites

Получение списка избранных объектов пользователя

#### POST /api/favorites

Добавление в избранное

```python
# Request
{
    "property_id": "uuid"
}
```

#### DELETE /api/favorites/{property_id}

Удаление из избранного

### 3.6 Отзывы

#### GET /api/reviews

Получение отзывов с фильтрацией

```python
# Query параметры
{
    "developer_id": "uuid",
    "property_id": "uuid",
    "rating_min": 4,
    "page": 1,
    "limit": 20
}
```

#### POST /api/reviews (Требует аутентификации)

Создание отзыва

#### PUT /api/reviews/{review_id} (Требует права)

Обновление отзыва

#### DELETE /api/reviews/{review_id} (Требует права)

Удаление отзыва

### 3.7 Заявки

#### POST /api/leads

Создание заявки

```python
# Request
{
    "property_id": "uuid",
    "name": "Иван Петров",
    "phone": "+79999999999",
    "email": "ivan@example.com",  # optional
    "message": "Хочу посмотреть квартиру",
    "lead_type": "VIEWING"
}
```

#### GET /api/leads (Требует права застройщика)

Получение заявок застройщика

#### PUT /api/leads/{lead_id}/status (Требует права)

Обновление статуса заявки

### 3.8 Аналитика и статистика

#### GET /api/analytics/popular-searches

Популярные поисковые запросы

#### GET /api/analytics/price-trends

Тренды цен по регионам

#### GET /api/properties/{property_id}/views

Статистика просмотров объекта

---

## 4. Технические требования

### 4.1 Валидация данных

- Номера телефонов в международном формате (+7XXXXXXXXXX)
- Email валидация по RFC 5322
- Обязательная валидация всех входящих данных
- Санитизация HTML в текстовых полях

### 4.2 Безопасность

- JWT токены с временем жизни 15 минут (access) и 7 дней (refresh)
- Rate limiting: 100 запросов в минуту для авторизованных, 20 для анонимных
- CORS настройка для фронтенд домена
- Хеширование паролей (если будут использоваться)
- Логирование всех операций изменения данных

### 4.3 Производительность

- Индексы на часто используемые поля (city, price, property_type, etc.)
- Кэширование популярных запросов в Redis на 5 минут
- Пагинация с максимумом 100 элементов на страницу
- Оптимизация запросов с использованием select_related/prefetch_related

### 4.4 Загрузка файлов

- Максимальный размер изображения: 10MB
- Поддерживаемые форматы изображений: JPG, PNG, WebP
- Максимальный размер документа: 50MB
- Поддерживаемые форматы документов: PDF, DOC, DOCX
- Автоматическое сжатие изображений
- Генерация thumbnails разных размеров

### 4.5 SMS-сервис

- Интеграция с SMS.RU или аналогичным провайдером
- Код подтверждения: 4 цифры
- Время жизни кода: 5 минут
- Ограничение: 3 попытки на номер в час

---

## 5. Обработка ошибок

### 5.1 HTTP статус коды

- **200** - Успешный запрос
- **201** - Создан новый ресурс
- **400** - Ошибка валидации данных
- **401** - Не авторизован
- **403** - Доступ запрещен
- **404** - Ресурс не найден
- **409** - Конфликт данных
- **422** - Ошибка валидации
- **429** - Превышен лимит запросов
- **500** - Внутренняя ошибка сервера

### 5.2 Формат ошибок

```python
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Некорректные данные",
        "details": {
            "phone": ["Номер телефона обязателен"]
        }
    }
}
```

---

## 6. Документация API

### 6.1 Swagger/OpenAPI

- Автоматическая генерация документации
- Интерактивная документация доступна по `/docs`
- Схемы данных и примеры запросов
- Описание всех endpoint'ов с параметрами

### 6.2 Postman Collection

- Экспорт коллекции для тестирования
- Примеры запросов для всех методов
- Переменные окружения для разных стендов

---

## 7. Мониторинг и логирование

### 7.1 Логирование

- Структурированные логи в JSON формате
- Уровни: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Логирование всех API запросов с временем выполнения
- Отдельные логи для ошибок валидации и безопасности

### 7.2 Метрики

- Количество запросов по endpoint'ам
- Время ответа API
- Количество ошибок по типам
- Статистика использования функций

---

## 8. Конфигурация и переменные окружения

```bash
# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/realestate
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# SMS
SMS_API_KEY=your-sms-api-key
SMS_SENDER=YourApp

# Файлы
MEDIA_URL=/media/
MEDIA_ROOT=/app/media/
MAX_UPLOAD_SIZE=52428800  # 50MB

# Rate Limiting
RATE_LIMIT_AUTHENTICATED=100/minute
RATE_LIMIT_ANONYMOUS=20/minute

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourapp.com
```

---

## 9. Развертывание

### 9.1 Docker Compose

```yaml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/realestate
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: realestate
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 9.2 Команды миграции

```bash
# Создание миграций
alembic revision --autogenerate -m "Create initial tables"

# Применение миграций
alembic upgrade head

# Создание суперпользователя
python -m app.create_superuser
```

---

## 10. Тестирование

### 10.1 Требования к тестам

- Покрытие тестами минимум 80%
- Unit тесты для всех моделей и сервисов
- Integration тесты для всех API endpoint'ов
- Тесты на производительность для критичных запросов

### 10.2 Фикстуры для тестов

- Тестовые пользователи разных ролей
- Тестовые объекты недвижимости
- Тестовые данные для различных сценариев

---

Данное ТЗ покрывает все основные требования к backend API для платформы недвижимости. API должен быть производительным, безопасным и готовым к масштабированию.
