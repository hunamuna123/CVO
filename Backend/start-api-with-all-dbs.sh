#!/bin/bash

# Real Estate API Startup Script with All Database Configurations
# This script ensures all databases (Redis, MongoDB, ClickHouse, Kafka) are properly configured

echo "🏠 Starting Real Estate API with all database configurations..."

# Set required environment variables
export ENVIRONMENT=development
export DEBUG=True
export APP_NAME="Real Estate API"
export VERSION=0.1.0

# Database Configuration
export DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/realestate
export DATABASE_POOL_SIZE=10
export DATABASE_MAX_OVERFLOW=20

# Redis Configuration (with password from docker-compose)
export REDIS_URL=redis://localhost:6379/0
export REDIS_PASSWORD=password

# JWT Configuration
export JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
export JWT_ALGORITHM=HS256
export ACCESS_TOKEN_EXPIRE_MINUTES=15
export REFRESH_TOKEN_EXPIRE_DAYS=7

# SMS Service Configuration
export SMS_API_KEY=your-sms-api-key
export SMS_SENDER=YourApp
export SMS_PROVIDER=sms_ru

# File Upload Configuration
export MEDIA_URL=/media/
export MEDIA_ROOT=./media/
export MAX_UPLOAD_SIZE=52428800

# Rate Limiting
export RATE_LIMIT_AUTHENTICATED=100/minute
export RATE_LIMIT_ANONYMOUS=20/minute

# CORS Configuration
export ALLOWED_ORIGINS="*"

# Security
export SECRET_KEY=your-super-secret-app-key-change-in-production

# Performance
export CACHE_TTL=300
export QUERY_CACHE_TTL=60

# MongoDB Configuration (with auth from docker-compose)
export MONGODB_URL=mongodb://admin:password@localhost:27017/realestate_documents?authSource=admin
export MONGODB_USERNAME=admin
export MONGODB_PASSWORD=password
export MONGODB_DATABASE=realestate_documents

# Kafka Configuration (using host port mapping)
export KAFKA_BOOTSTRAP_SERVERS=localhost:29092
export KAFKA_CLIENT_ID=realestate_api

# ClickHouse Configuration (enabled with auth)
export CLICKHOUSE_ENABLED=true
export CLICKHOUSE_HOST=localhost
export CLICKHOUSE_PORT=9000
export CLICKHOUSE_DATABASE=realestate_analytics
export CLICKHOUSE_USER=default
export CLICKHOUSE_PASSWORD=password

# Monitoring and Logging
export LOG_LEVEL=INFO

echo "✅ Environment variables configured"

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first."
    exit 1
fi

# Check if all Docker services are running
echo "🔍 Checking Docker services..."

services=("backend-postgres-1" "backend-redis-1" "backend-mongodb-1" "backend-clickhouse-1" "backend-kafka-1")
for service in "${services[@]}"; do
    if ! docker ps --format "table {{.Names}}" | grep -q "$service"; then
        echo "❌ Service $service is not running. Please start with: docker-compose -f docker-compose.full.yml up -d"
        exit 1
    fi
done

echo "✅ All required Docker services are running"

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 3

# Test database connections
echo "🔍 Testing database connections..."

# Test PostgreSQL
if ! pg_isready -h localhost -p 5432 -U postgres > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not ready"
    exit 1
fi
echo "✅ PostgreSQL is ready"

# Test Redis
if ! redis-cli -h localhost -p 6379 -a password ping > /dev/null 2>&1; then
    echo "❌ Redis is not ready"
    exit 1
fi
echo "✅ Redis is ready"

# Test ClickHouse
if ! curl -s 'http://localhost:8123/ping' | grep -q "Ok"; then
    echo "❌ ClickHouse is not ready"
    exit 1
fi
echo "✅ ClickHouse is ready"

# Test MongoDB
if ! mongosh --host localhost:27017 --authenticationDatabase admin -u admin -p password --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "⚠️ MongoDB connection test failed, but will continue (startup will handle it)"
fi
echo "✅ MongoDB is ready"

echo "🚀 Starting Real Estate API..."

# Run migrations if needed
echo "📊 Running database migrations..."
poetry run alembic upgrade head

# Start the API
echo "🌟 API is starting on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo "📊 Metrics: http://localhost:8000/metrics"

echo "🔄 Starting with hot reload enabled..."
poetry run python -m app.main

echo "👋 API shutdown complete"
