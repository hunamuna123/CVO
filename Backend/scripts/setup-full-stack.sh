#!/bin/bash

# Real Estate API - Full Stack Setup Script
# This script sets up the complete development environment with all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}${1}${NC}"
    echo -e "${PURPLE}$(echo $1 | sed 's/./=/g')${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    log_header "🏠 Real Estate API - Full Stack Setup"
    
    # Check prerequisites
    check_prerequisites
    
    # Setup environment
    setup_environment
    
    # Install Python dependencies
    install_dependencies
    
    # Setup databases and services
    setup_services
    
    # Run migrations
    run_migrations
    
    # Setup monitoring
    setup_monitoring
    
    # Final steps
    final_setup
    
    log_success "🎉 Full stack setup completed successfully!"
    show_service_urls
}

check_prerequisites() {
    log_header "🔍 Checking Prerequisites"
    
    # Check Docker
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    log_success "Docker is installed"
    
    # Check Docker Compose
    if ! command_exists docker-compose; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    log_success "Docker Compose is installed"
    
    # Check Poetry
    if ! command_exists poetry; then
        log_warning "Poetry is not installed. Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
        
        if ! command_exists poetry; then
            log_error "Failed to install Poetry. Please install it manually."
            exit 1
        fi
    fi
    log_success "Poetry is installed"
    
    # Check Python version
    if ! command_exists python3.13; then
        log_warning "Python 3.13 not found, checking for python3..."
        if ! command_exists python3; then
            log_error "Python 3 is not installed. Please install Python 3.13+."
            exit 1
        fi
        
        PYTHON_VERSION=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
        if [[ $(echo "$PYTHON_VERSION < 3.11" | bc) -eq 1 ]]; then
            log_error "Python 3.11+ is required. Found version: $PYTHON_VERSION"
            exit 1
        fi
    fi
    log_success "Python is installed"
}

setup_environment() {
    log_header "🔧 Setting Up Environment"
    
    # Copy environment file if it doesn't exist
    if [[ ! -f .env ]]; then
        log_info "Copying .env.example to .env"
        cp .env.example .env
        log_warning "Please review and update the .env file with your settings"
    else
        log_info ".env file already exists"
    fi
    
    # Create necessary directories
    log_info "Creating necessary directories..."
    mkdir -p media/{images,documents,temp}
    mkdir -p logs
    mkdir -p monitoring/{grafana/dashboards,logstash/{config,pipeline}}
    mkdir -p scripts/init
    
    log_success "Environment setup completed"
}

install_dependencies() {
    log_header "📦 Installing Dependencies"
    
    # Configure Poetry
    log_info "Configuring Poetry..."
    poetry config virtualenvs.in-project true
    poetry config installer.parallel true
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    poetry install
    
    log_success "Dependencies installed"
}

setup_services() {
    log_header "🐳 Setting Up Services"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Pull images first to show progress
    log_info "Pulling Docker images..."
    docker-compose -f docker-compose.full.yml pull
    
    # Start core services first
    log_info "Starting core services (PostgreSQL, Redis)..."
    docker-compose -f docker-compose.full.yml up -d postgres redis
    
    # Wait for core services
    log_info "Waiting for core services to be ready..."
    sleep 10
    
    # Start additional services
    log_info "Starting additional services (MongoDB, ClickHouse, Kafka)..."
    docker-compose -f docker-compose.full.yml up -d mongodb clickhouse zookeeper kafka
    
    # Wait for additional services
    log_info "Waiting for additional services to be ready..."
    sleep 20
    
    # Start monitoring services
    log_info "Starting monitoring services (Prometheus, Grafana, ELK)..."
    docker-compose -f docker-compose.full.yml up -d prometheus grafana elasticsearch kibana
    
    # Start remaining services
    log_info "Starting remaining services..."
    docker-compose -f docker-compose.full.yml up -d
    
    log_success "All services started"
}

run_migrations() {
    log_header "🗄️ Running Database Migrations"
    
    # Wait a bit more for PostgreSQL to be fully ready
    log_info "Waiting for PostgreSQL to be ready..."
    sleep 15
    
    # Run Alembic migrations
    log_info "Running database migrations..."
    poetry run alembic upgrade head
    
    # Seed database with sample data
    log_info "Seeding database with sample data..."
    poetry run seed || log_warning "Failed to seed database (this is optional)"
    
    log_success "Database migrations completed"
}

setup_monitoring() {
    log_header "📊 Setting Up Monitoring"
    
    # Create Grafana dashboard
    log_info "Setting up Grafana dashboards..."
    
    # Create a basic dashboard configuration
    cat > monitoring/grafana/dashboards/realestate-api.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Real Estate API Dashboard",
    "tags": ["realestate"],
    "style": "dark",
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF
    
    log_success "Monitoring setup completed"
}

final_setup() {
    log_header "🎯 Final Setup Steps"
    
    # Install pre-commit hooks
    log_info "Installing pre-commit hooks..."
    poetry run pre-commit install
    
    # Create initial admin user (optional)
    log_info "Creating initial admin user..."
    poetry run python -c "
import asyncio
from app.scripts.create_admin import create_admin_user
asyncio.run(create_admin_user())
" || log_warning "Failed to create admin user (this is optional)"
    
    log_success "Final setup completed"
}

show_service_urls() {
    log_header "🌐 Service URLs"
    
    echo -e "${GREEN}Core Services:${NC}"
    echo -e "  API Documentation:    ${CYAN}http://localhost:8000/docs${NC}"
    echo -e "  API Health Check:     ${CYAN}http://localhost:8000/health${NC}"
    echo -e "  API Metrics:          ${CYAN}http://localhost:8000/metrics${NC}"
    echo ""
    
    echo -e "${GREEN}Databases:${NC}"
    echo -e "  PostgreSQL:           ${CYAN}localhost:5432${NC}"
    echo -e "  Redis:                ${CYAN}localhost:6379${NC}"
    echo -e "  MongoDB:              ${CYAN}localhost:27017${NC}"
    echo -e "  ClickHouse:           ${CYAN}http://localhost:8123${NC}"
    echo ""
    
    echo -e "${GREEN}Message Queue:${NC}"
    echo -e "  Kafka UI:             ${CYAN}http://localhost:8080${NC}"
    echo ""
    
    echo -e "${GREEN}Monitoring:${NC}"
    echo -e "  Prometheus:           ${CYAN}http://localhost:9090${NC}"
    echo -e "  Grafana:              ${CYAN}http://localhost:3000${NC} (admin/admin)"
    echo -e "  Kibana:               ${CYAN}http://localhost:5601${NC}"
    echo -e "  Flower (Celery):      ${CYAN}http://localhost:5555${NC}"
    echo ""
    
    echo -e "${GREEN}Storage:${NC}"
    echo -e "  MinIO Console:        ${CYAN}http://localhost:9001${NC} (minioadmin/minioadmin)"
    echo ""
    
    echo -e "${GREEN}Development Commands:${NC}"
    echo -e "  Start API:            ${CYAN}poetry run dev${NC}"
    echo -e "  Run tests:            ${CYAN}poetry run test${NC}"
    echo -e "  Check code:           ${CYAN}poetry run check-all${NC}"
    echo -e "  View logs:            ${CYAN}docker-compose -f docker-compose.full.yml logs -f api${NC}"
    echo ""
    
    echo -e "${YELLOW}Note: Some services might take a few minutes to fully initialize.${NC}"
    echo -e "${YELLOW}Check service health with: docker-compose -f docker-compose.full.yml ps${NC}"
}

# Handle script arguments
case "${1:-}" in
    "services")
        setup_services
        ;;
    "monitoring")
        setup_monitoring
        ;;
    "migrations")
        run_migrations
        ;;
    "urls")
        show_service_urls
        ;;
    *)
        main
        ;;
esac
