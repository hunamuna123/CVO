#!/bin/bash

# Real Estate Platform Backend - Development Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 Setting up Real Estate Platform Backend Development Environment"
echo "=================================================================="

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ Poetry found"

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Copy environment file if not exists
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
else
    echo "✅ .env file already exists"
fi

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL service."
    echo "   On Ubuntu/Debian: sudo systemctl start postgresql"
    echo "   On macOS: brew services start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Check if Redis is running
if ! redis-cli ping &> /dev/null; then
    echo "⚠️  Redis is not running. Please start Redis service."
    echo "   On Ubuntu/Debian: sudo systemctl start redis"
    echo "   On macOS: brew services start redis"
    exit 1
fi

echo "✅ Redis is running"

# Create database if it doesn't exist
DB_NAME="realestate"
if ! psql -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "🗄️  Creating database '$DB_NAME'..."
    createdb $DB_NAME
else
    echo "✅ Database '$DB_NAME' already exists"
fi

# Run migrations
echo "🔄 Running database migrations..."
poetry run alembic upgrade head

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
poetry run pre-commit install

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env file with your configuration"
echo "   2. Start the development server:"
echo "      poetry run uvicorn app.main:app --reload"
echo "   3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "🐳 Alternative: Use Docker for development:"
echo "   docker-compose up -d"
echo ""
echo "🧪 Run tests:"
echo "   poetry run pytest"
echo ""
echo "📚 For more information, see README.md"
