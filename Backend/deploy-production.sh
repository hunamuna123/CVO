#!/bin/bash

# Real Estate API Production Deployment Script
# This script deploys the API to production using Docker containers

set -e  # Exit on any error

echo "🚀 Starting Real Estate API Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env.production.local exists
if [ ! -f ".env.production.local" ]; then
    print_warning ".env.production.local not found!"
    print_status "Creating .env.production.local from template..."
    
    if [ -f ".env.production" ]; then
        cp .env.production .env.production.local
        print_warning "Please edit .env.production.local and update all passwords and secrets before continuing!"
        print_warning "Run: nano .env.production.local"
        exit 1
    else
        print_error ".env.production template not found!"
        exit 1
    fi
fi

# Function to generate secure passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Ask user if they want to generate new passwords
read -p "Do you want to generate new secure passwords? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Generating secure passwords..."
    
    # Generate passwords
    POSTGRES_PWD=$(generate_password)
    REDIS_PWD=$(generate_password)
    MONGODB_PWD=$(generate_password)
    CLICKHOUSE_PWD=$(generate_password)
    JWT_SECRET=$(generate_password)$(generate_password)  # Extra long for JWT
    SECRET_KEY=$(generate_password)$(generate_password)
    FLOWER_PWD=$(generate_password)
    
    # Update .env.production.local
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=${POSTGRES_PWD}/" .env.production.local
    sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=${REDIS_PWD}/" .env.production.local
    sed -i "s/MONGODB_PASSWORD=.*/MONGODB_PASSWORD=${MONGODB_PWD}/" .env.production.local
    sed -i "s/CLICKHOUSE_PASSWORD=.*/CLICKHOUSE_PASSWORD=${CLICKHOUSE_PWD}/" .env.production.local
    sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=${JWT_SECRET}/" .env.production.local
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env.production.local
    sed -i "s/FLOWER_PASSWORD=.*/FLOWER_PASSWORD=${FLOWER_PWD}/" .env.production.local
    
    print_success "Passwords generated and saved to .env.production.local"
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p media logs nginx/conf.d

# Set proper permissions
print_status "Setting file permissions..."
chmod +x deploy-production.sh

# Stop any existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.production.yml --env-file .env.production.local down || true

# Pull latest images
print_status "Pulling latest Docker images..."
docker-compose -f docker-compose.production.yml --env-file .env.production.local pull

# Build the application image
print_status "Building application Docker image..."
docker-compose -f docker-compose.production.yml --env-file .env.production.local build --no-cache

# Start the services
print_status "Starting services in production mode..."
docker-compose -f docker-compose.production.yml --env-file .env.production.local up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check service health
print_status "Checking service health..."

# Check if API is responding
if curl -f http://localhost:8000/health &>/dev/null; then
    print_success "API is healthy and responding"
else
    print_warning "API health check failed, checking logs..."
    docker-compose -f docker-compose.production.yml --env-file .env.production.local logs api
fi

# Show running containers
print_status "Running containers:"
docker-compose -f docker-compose.production.yml --env-file .env.production.local ps

print_success "Deployment completed!"
print_status "API is available at: http://$(hostname -I | awk '{print $1}'):80"
print_status "API Documentation: http://$(hostname -I | awk '{print $1}'):80/docs"
print_status "Flower (Celery Monitor): http://$(hostname -I | awk '{print $1}'):5555"
print_status ""
print_status "To view logs: docker-compose -f docker-compose.production.yml --env-file .env.production.local logs -f"
print_status "To stop: docker-compose -f docker-compose.production.yml --env-file .env.production.local down"
print_status "To restart: docker-compose -f docker-compose.production.yml --env-file .env.production.local restart"

echo "✅ Deployment script completed successfully!"
