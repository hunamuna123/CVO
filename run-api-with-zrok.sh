#!/bin/bash

# Real Estate API with zrok - Production Startup Script
# This script manages the API lifecycle with persistent zrok tunneling

set -e

# Configuration
API_PORT=8000
ZROK_CONFIG_FILE="$HOME/.zrok/zrok_share_config.json"
ZROK_PID_FILE="/tmp/zrok_api.pid"
API_PID_FILE="/tmp/api.pid"
LOG_DIR="./logs"
API_LOG_FILE="$LOG_DIR/api.log"
ZROK_LOG_FILE="$LOG_DIR/zrok.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emoji
ROCKET="🚀"
CHECK="✅"
CROSS="❌"
WARNING="⚠️"
INFO="ℹ️"
GLOBE="🌐"

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}${CHECK}${NC} $1"
}

error() {
    echo -e "${RED}${CROSS}${NC} $1"
}

warning() {
    echo -e "${YELLOW}${WARNING}${NC} $1"
}

info() {
    echo -e "${BLUE}${INFO}${NC} $1"
}

# Create log directory
mkdir -p "$LOG_DIR"

# Function to check if process is running
is_process_running() {
    local pid_file="$1"
    if [[ -f "$pid_file" ]]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# Function to stop processes
stop_processes() {
    log "Stopping all processes..."
    
    # Stop API
    if is_process_running "$API_PID_FILE"; then
        local api_pid=$(cat "$API_PID_FILE")
        log "Stopping API process (PID: $api_pid)..."
        kill "$api_pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$api_pid" 2>/dev/null; then
            warning "Force killing API process..."
            kill -9 "$api_pid" 2>/dev/null || true
        fi
        rm -f "$API_PID_FILE"
        success "API stopped"
    fi
    
    # Stop zrok
    if is_process_running "$ZROK_PID_FILE"; then
        local zrok_pid=$(cat "$ZROK_PID_FILE")
        log "Stopping zrok process (PID: $zrok_pid)..."
        kill "$zrok_pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$zrok_pid" 2>/dev/null; then
            warning "Force killing zrok process..."
            kill -9 "$zrok_pid" 2>/dev/null || true
        fi
        rm -f "$ZROK_PID_FILE"
        success "zrok stopped"
    fi
    
    # Kill any remaining python/uvicorn processes related to our API
    pkill -f "app.main" 2>/dev/null || true
    pkill -f "uvicorn.*app.main" 2>/dev/null || true
}

# Function to check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    # Check Poetry
    if ! command -v poetry &> /dev/null; then
        error "Poetry is not installed. Please install it first."
        exit 1
    fi
    success "Poetry is available"
    
    # Check zrok
    if ! command -v zrok &> /dev/null; then
        error "zrok is not installed. Please install it first."
        exit 1
    fi
    success "zrok is available"
    
    # Check if zrok is configured
    if ! zrok status &> /dev/null; then
        error "zrok is not configured. Please run 'zrok enable' first."
        exit 1
    fi
    success "zrok is configured"
    
    # Check if Docker services are running
    local required_services=("backend-postgres-1" "backend-redis-1" "backend-mongodb-1" "backend-clickhouse-1" "backend-kafka-1")
    local missing_services=()
    
    for service in "${required_services[@]}"; do
        if ! docker ps --format "table {{.Names}}" | grep -q "$service"; then
            missing_services+=("$service")
        fi
    done
    
    if [ ${#missing_services[@]} -ne 0 ]; then
        warning "Some Docker services are not running: ${missing_services[*]}"
        info "Starting missing services..."
        docker-compose -f docker-compose.full.yml up -d
        sleep 5
        success "Docker services started"
    else
        success "All Docker services are running"
    fi
}

# Function to wait for API to be ready
wait_for_api() {
    log "Waiting for API to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "http://localhost:$API_PORT/health" > /dev/null 2>&1; then
            success "API is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    error "API failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Function to get or create persistent zrok share
get_zrok_share() {
    log "Setting up zrok share..."
    
    # Check if we have a saved share token
    if [[ -f "$ZROK_CONFIG_FILE" ]]; then
        local saved_token=$(jq -r '.share_token // empty' "$ZROK_CONFIG_FILE" 2>/dev/null || echo "")
        if [[ -n "$saved_token" && "$saved_token" != "null" ]]; then
            info "Found saved zrok share token: $saved_token"
            # Verify the token still exists
            local token_part=$(echo $saved_token | sed 's|https://||' | sed 's|\.share\.zrok\.io||')
            if zrok overview | jq -e ".environments[].shares[] | select(.shareToken == \"$token_part\")" > /dev/null 2>&1; then
                echo "$saved_token"
                return 0
            else
                warning "Saved token no longer valid, removing..."
                rm -f "$ZROK_CONFIG_FILE"
            fi
        fi
    fi
    
    # Create new reserved share
    log "Creating new zrok reserved share..."
    local share_output
    share_output=$(zrok reserve public --unique-name "realestate-api-$(date +%s)" http://localhost:$API_PORT 2>&1)
    
    if [[ $? -eq 0 ]]; then
        # Extract the share token from the output
        local share_token=$(echo "$share_output" | grep -oP 'https://[a-zA-Z0-9]+\.share\.zrok\.io' | head -n1)
        if [[ -n "$share_token" ]]; then
            # Save the share token
            mkdir -p "$(dirname "$ZROK_CONFIG_FILE")"
            local token_only=$(echo "$share_token" | sed 's|https://||' | sed 's|\.share\.zrok\.io||')
            echo "{\"share_token\": \"$share_token\", \"token_only\": \"$token_only\", \"created_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$ZROK_CONFIG_FILE"
            success "Created new zrok share: $share_token"
            echo "$share_token"
            return 0
        fi
    fi
    
    # Fallback to temporary share
    warning "Failed to create reserved share, using temporary share..."
    echo "temporary"
}

# Function to start zrok share
start_zrok() {
    log "Starting zrok share..."
    
    # Always try to use temporary share first to avoid token issues
    log "Using temporary zrok share for reliability..."
    
    # Start temporary share
    zrok share public --headless "http://localhost:$API_PORT" > "$ZROK_LOG_FILE" 2>&1 &
    local zrok_pid=$!
    echo "$zrok_pid" > "$ZROK_PID_FILE"
    
    # Wait for zrok to start and get the URL
    log "Waiting for zrok to generate URL..."
    local max_attempts=15
    local attempt=1
    local zrok_url=""
    
    while [ $attempt -le $max_attempts ]; do
        if [[ -f "$ZROK_LOG_FILE" ]]; then
            zrok_url=$(grep -oP 'https://[a-zA-Z0-9]+\.share\.zrok\.io' "$ZROK_LOG_FILE" | head -n1)
            if [[ -n "$zrok_url" ]]; then
                break
            fi
        fi
        
        # Check if process is still running
        if ! kill -0 "$zrok_pid" 2>/dev/null; then
            error "zrok process died during startup"
            cat "$ZROK_LOG_FILE"
            return 1
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    if [[ -n "$zrok_url" ]]; then
        success "zrok share started: $zrok_url"
        
        # Save the URL for reference
        mkdir -p "$(dirname "$ZROK_CONFIG_FILE")"
        echo "{\"share_token\": \"$zrok_url\", \"created_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"type\": \"temporary\"}" > "$ZROK_CONFIG_FILE"
        
        echo "$zrok_url"
        return 0
    else
        error "Failed to get zrok URL after $((max_attempts * 2)) seconds"
        if [[ -f "$ZROK_LOG_FILE" ]]; then
            error "zrok logs:"
            cat "$ZROK_LOG_FILE"
        fi
        return 1
    fi
}

# Function to start API
start_api() {
    log "Starting Real Estate API..."
    
    # Set environment variables for all databases
    export ENVIRONMENT=development
    export DEBUG=True
    export DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/realestate
    export REDIS_URL=redis://localhost:6379/0
    export REDIS_PASSWORD=password
    export MONGODB_URL=mongodb://admin:password@localhost:27017/realestate_documents?authSource=admin
    export CLICKHOUSE_ENABLED=true
    export CLICKHOUSE_HOST=localhost
    export CLICKHOUSE_PORT=9000
    export CLICKHOUSE_DATABASE=realestate_analytics
    export CLICKHOUSE_USER=default
    export CLICKHOUSE_PASSWORD=password
    export KAFKA_BOOTSTRAP_SERVERS=localhost:29092
    export KAFKA_CLIENT_ID=realestate_api
    export JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
    export JWT_ALGORITHM=HS256
    export ACCESS_TOKEN_EXPIRE_MINUTES=15
    export REFRESH_TOKEN_EXPIRE_DAYS=7
    
    # Start API with Poetry
    cd /home/keiske/CVO/Backend
    poetry run uvicorn app.main:app --host 0.0.0.0 --port $API_PORT --log-level info > "$API_LOG_FILE" 2>&1 &
    local api_pid=$!
    echo "$api_pid" > "$API_PID_FILE"
    
    # Wait for API to be ready
    if wait_for_api; then
        success "API started successfully (PID: $api_pid)"
        return 0
    else
        error "API failed to start"
        cat "$API_LOG_FILE"
        return 1
    fi
}

# Function to show status
show_status() {
    echo
    echo -e "${BLUE}========================================${NC}"
    echo -e "${ROCKET} ${GREEN}Real Estate API Status${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # API Status
    if is_process_running "$API_PID_FILE"; then
        local api_pid=$(cat "$API_PID_FILE")
        success "API is running (PID: $api_pid)"
        echo -e "   ${INFO} Local URL: http://localhost:$API_PORT"
        echo -e "   ${INFO} Health: http://localhost:$API_PORT/health"
        echo -e "   ${INFO} Docs: http://localhost:$API_PORT/docs"
    else
        error "API is not running"
    fi
    
    # zrok Status
    if is_process_running "$ZROK_PID_FILE"; then
        local zrok_pid=$(cat "$ZROK_PID_FILE")
        success "zrok is running (PID: $zrok_pid)"
        
        # Get zrok URL
        if [[ -f "$ZROK_CONFIG_FILE" ]]; then
            local zrok_url=$(jq -r '.share_token // empty' "$ZROK_CONFIG_FILE" 2>/dev/null || echo "")
            if [[ -n "$zrok_url" ]]; then
                echo -e "   ${GLOBE} Public URL: $zrok_url"
                echo -e "   ${GLOBE} Public Health: $zrok_url/health"
                echo -e "   ${GLOBE} Public Docs: $zrok_url/docs"
            fi
        fi
        
        # Try to get URL from logs as fallback
        if [[ -f "$ZROK_LOG_FILE" ]]; then
            local temp_url=$(grep -oP 'https://[a-zA-Z0-9]+\.share\.zrok\.io' "$ZROK_LOG_FILE" | head -n1)
            if [[ -n "$temp_url" && -z "$zrok_url" ]]; then
                echo -e "   ${GLOBE} Temporary URL: $temp_url"
            fi
        fi
    else
        error "zrok is not running"
    fi
    
    # Database Status
    echo
    if curl -s "http://localhost:$API_PORT/health" > /dev/null 2>&1; then
        local health_status=$(curl -s "http://localhost:$API_PORT/health" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
        if [[ "$health_status" == "healthy" ]]; then
            success "All databases are healthy"
        else
            warning "Some databases may have issues"
        fi
    fi
    
    echo -e "${BLUE}========================================${NC}"
    echo
}

# Function to handle cleanup on exit
cleanup() {
    echo
    log "Received interrupt signal, cleaning up..."
    stop_processes
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
case "${1:-start}" in
    "start")
        log "Starting Real Estate API with zrok..."
        
        # Stop any existing processes
        stop_processes
        
        # Check dependencies
        check_dependencies
        
        # Start API
        if start_api; then
            # Start zrok
            if start_zrok; then
                show_status
                
                # Keep script running and monitor processes
                log "Monitoring processes... Press Ctrl+C to stop"
                while true; do
                    # Check if API is still running
                    if ! is_process_running "$API_PID_FILE"; then
                        error "API process died, restarting..."
                        start_api
                    fi
                    
                    # Check if zrok is still running
                    if ! is_process_running "$ZROK_PID_FILE"; then
                        warning "zrok process died, restarting..."
                        start_zrok
                    fi
                    
                    sleep 10
                done
            else
                error "Failed to start zrok"
                stop_processes
                exit 1
            fi
        else
            error "Failed to start API"
            exit 1
        fi
        ;;
    
    "stop")
        stop_processes
        success "All processes stopped"
        ;;
    
    "restart")
        log "Restarting Real Estate API with zrok..."
        stop_processes
        sleep 2
        exec "$0" start
        ;;
    
    "status")
        show_status
        ;;
    
    "logs")
        if [[ "${2:-api}" == "api" ]]; then
            log "Showing API logs..."
            tail -f "$API_LOG_FILE"
        elif [[ "$2" == "zrok" ]]; then
            log "Showing zrok logs..."
            tail -f "$ZROK_LOG_FILE"
        else
            error "Usage: $0 logs [api|zrok]"
            exit 1
        fi
        ;;
    
    "url")
        if [[ -f "$ZROK_CONFIG_FILE" ]]; then
            local zrok_url=$(jq -r '.share_token // empty' "$ZROK_CONFIG_FILE" 2>/dev/null || echo "")
            if [[ -n "$zrok_url" ]]; then
                echo "$zrok_url"
            else
                error "No saved zrok URL found"
                exit 1
            fi
        else
            error "No zrok configuration found"
            exit 1
        fi
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [api|zrok]|url}"
        echo
        echo "Commands:"
        echo "  start   - Start API and zrok (default)"
        echo "  stop    - Stop all processes"
        echo "  restart - Restart everything"
        echo "  status  - Show current status"
        echo "  logs    - Show logs (api or zrok)"
        echo "  url     - Show zrok public URL"
        exit 1
        ;;
esac
