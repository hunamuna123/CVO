#!/bin/bash

# Deploy Real Estate API to Remote Server
# This script copies files to the server and runs the deployment

set -e

# Server configuration
SERVER_USER="root"
SERVER_HOST="85.175.100.129"
SERVER_PATH="/opt/realestate-api"
LOCAL_PATH="/home/keiske/CVO/Backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
    print_warning "No SSH key found. You'll need to enter password for each connection."
fi

print_status "🚀 Starting deployment to server $SERVER_HOST..."

# Test SSH connection
print_status "Testing SSH connection..."
if ssh -o ConnectTimeout=10 -o BatchMode=yes $SERVER_USER@$SERVER_HOST exit 2>/dev/null; then
    print_success "SSH connection successful"
else
    print_warning "SSH key authentication failed, will use password authentication"
fi

# Create directory on server
print_status "Creating directory on server..."
ssh $SERVER_USER@$SERVER_HOST "mkdir -p $SERVER_PATH"

# Sync files to server (excluding unnecessary files)
print_status "Syncing files to server..."
rsync -avz --progress \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='logs' \
    --exclude='media' \
    --exclude='.env' \
    --exclude='api.log' \
    $LOCAL_PATH/ $SERVER_USER@$SERVER_HOST:$SERVER_PATH/

print_success "Files synced successfully"

# Install Docker if not present
print_status "Checking Docker installation on server..."
ssh $SERVER_USER@$SERVER_HOST "
if ! command -v docker &> /dev/null; then
    echo 'Installing Docker...'
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
    rm get-docker.sh
    echo 'Docker installed successfully'
else
    echo 'Docker is already installed'
fi
"

# Install Docker Compose if not present
print_status "Checking Docker Compose installation on server..."
ssh $SERVER_USER@$SERVER_HOST "
if ! command -v docker-compose &> /dev/null; then
    echo 'Installing Docker Compose...'
    curl -L \"https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo 'Docker Compose installed successfully'
else
    echo 'Docker Compose is already installed'
fi
"

# Make deployment script executable
ssh $SERVER_USER@$SERVER_HOST "chmod +x $SERVER_PATH/deploy-production.sh"

# Run deployment on server
print_status "Running deployment on server..."
ssh -t $SERVER_USER@$SERVER_HOST "cd $SERVER_PATH && ./deploy-production.sh"

print_success "🎉 Deployment to server completed successfully!"
print_status ""
print_status "Your API is now running on: http://$SERVER_HOST"
print_status "API Documentation: http://$SERVER_HOST/docs"
print_status "Health Check: http://$SERVER_HOST/health"
print_status "Flower Monitor: http://$SERVER_HOST:5555"
print_status ""
print_status "To connect to server: ssh $SERVER_USER@$SERVER_HOST"
print_status "Application directory: $SERVER_PATH"
print_status ""
print_status "Useful commands on server:"
print_status "  View logs: cd $SERVER_PATH && docker-compose -f docker-compose.production.yml logs -f"
print_status "  Restart: cd $SERVER_PATH && docker-compose -f docker-compose.production.yml restart"
print_status "  Stop: cd $SERVER_PATH && docker-compose -f docker-compose.production.yml down"
