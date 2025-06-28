# Real Estate Platform Backend API - Development Makefile

.PHONY: help install dev start test lint format clean build docker requirements

# Default target
help: ## Show this help message
	@echo "🏗️  Real Estate Platform Backend API"
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Setup and Installation
install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies..."
	poetry install

install-pre-commit: ## Install pre-commit hooks
	@echo "🔧 Installing pre-commit hooks..."
	poetry run pre-commit install

setup: install install-pre-commit ## Complete project setup
	@echo "✅ Project setup complete!"

# Development
dev: ## Start development server
	@echo "🚀 Starting development server..."
	poetry run dev

start: ## Start production server
	@echo "🚀 Starting production server..."
	poetry run start

shell: ## Open Poetry shell
	@echo "🐚 Opening Poetry shell..."
	poetry shell

# Database
migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	poetry run migrate

seed: ## Seed database with sample data
	@echo "🌱 Seeding database..."
	poetry run seed

init-db: ## Initialize database (migrate + seed)
	@echo "🗄️ Initializing database..."
	poetry run init-db

# Testing and Quality
test: ## Run tests with coverage
	@echo "🧪 Running tests..."
	poetry run test

test-watch: ## Run tests in watch mode
	@echo "👀 Running tests in watch mode..."
	poetry run pytest --looponfail

lint: ## Run code linting
	@echo "🔍 Running linting..."
	poetry run lint

format: ## Format code with black and isort
	@echo "✨ Formatting code..."
	poetry run format

check: format lint test ## Run all code quality checks
	@echo "✅ All checks completed!"

# Maintenance
clean: ## Clean up build artifacts and cache
	@echo "🧹 Cleaning up..."
	poetry run clean

requirements: ## Export requirements.txt
	@echo "📋 Exporting requirements.txt..."
	poetry run requirements

build: ## Build the application
	@echo "🏗️ Building application..."
	poetry run build

# Docker
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t realestate-api .

docker-run: ## Run application in Docker
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 --env-file .env realestate-api

docker-up: ## Start services with docker-compose
	@echo "🐳 Starting services with docker-compose..."
	docker-compose up -d

docker-down: ## Stop services with docker-compose
	@echo "🐳 Stopping services..."
	docker-compose down

docker-logs: ## View docker-compose logs
	@echo "🐳 Viewing logs..."
	docker-compose logs -f

# Logs and Monitoring
logs: ## Show application logs
	@echo "📋 Showing logs..."
	poetry run show-logs

# Environment
env-example: ## Create example environment file
	@echo "📝 Creating .env.example..."
	@if [ ! -f .env.example ]; then \
		cp .env .env.example; \
		echo "✅ Created .env.example from .env"; \
	else \
		echo "ℹ️  .env.example already exists"; \
	fi

# Quick commands
run: dev ## Alias for dev command

server: start ## Alias for start command

t: test ## Shorthand for test

l: lint ## Shorthand for lint

f: format ## Shorthand for format

c: clean ## Shorthand for clean

# Project status
status: ## Show project status
	@echo "📊 Project Status:"
	@echo "Poetry version: $$(poetry --version)"
	@echo "Python version: $$(poetry run python --version)"
	@echo "Virtual environment: $$(poetry env info --path)"
	@echo "Dependencies: $$(poetry show | wc -l) packages installed"
	@if [ -d ".git" ]; then echo "Git branch: $$(git branch --show-current)"; fi

info: status ## Alias for status

# Update dependencies
update: ## Update dependencies
	@echo "📦 Updating dependencies..."
	poetry update

outdated: ## Show outdated dependencies
	@echo "📦 Checking for outdated dependencies..."
	poetry show --outdated
