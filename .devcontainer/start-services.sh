#!/bin/bash

# Startup script for Dev Container
# This script starts all services needed for development

set -e

echo "========================================"
echo "  Keycloak Auth Service - Dev Container"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if we're in the devcontainer
if [ ! -d "/workspace" ]; then
    print_error "This script should be run inside the Dev Container"
    exit 1
fi

cd /workspace

echo "Starting services..."
echo ""

# Option to start specific services
case "${1:-all}" in
    keycloak)
        echo "Starting Keycloak only..."
        docker-compose up -d keycloak keycloak-init
        print_status "Keycloak starting at http://localhost:8080"
        ;;
    backend)
        echo "Starting Auth Service..."
        cd /workspace/auth-service
        if [ ! -d "venv" ]; then
            print_warning "Creating virtual environment..."
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt -q
        print_status "Starting auth-service on port 5000..."
        python run.py &
        ;;
    frontend)
        echo "Starting Frontend..."
        cd /workspace/frontend
        if [ ! -d "node_modules" ]; then
            print_warning "Installing npm dependencies..."
            npm install
        fi
        print_status "Starting frontend on port 3000..."
        npm run dev &
        ;;
    all)
        echo "Starting all services..."
        echo ""

        # Start Keycloak
        print_status "Starting Keycloak..."
        docker-compose up -d keycloak keycloak-init

        echo ""
        echo "Waiting for Keycloak to be ready (this may take 30-60 seconds)..."
        sleep 10

        # Start Backend
        print_status "Setting up Auth Service..."
        cd /workspace/auth-service
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -r requirements.txt -q

        # Start Frontend
        print_status "Setting up Frontend..."
        cd /workspace/frontend
        if [ ! -d "node_modules" ]; then
            npm install --silent
        fi

        echo ""
        echo "========================================"
        echo "  All services configured!"
        echo "========================================"
        echo ""
        echo "To start the services, open separate terminals:"
        echo ""
        echo "  Terminal 1 (Backend):"
        echo "    cd /workspace/auth-service"
        echo "    source venv/bin/activate"
        echo "    python run.py"
        echo ""
        echo "  Terminal 2 (Frontend):"
        echo "    cd /workspace/frontend"
        echo "    npm run dev"
        echo ""
        echo "Access points:"
        echo "  - Frontend:    http://localhost:3000"
        echo "  - Auth API:    http://localhost:5000"
        echo "  - Swagger UI:  http://localhost:5000/swagger-ui"
        echo "  - Keycloak:    http://localhost:8080 (admin/admin)"
        echo ""
        echo "Test users:"
        echo "  - testuser / password123 (role: user)"
        echo "  - adminuser / admin123 (roles: user, admin)"
        echo ""
        ;;
    status)
        echo "Checking service status..."
        echo ""

        # Check Keycloak
        if curl -s http://localhost:8080/health/ready > /dev/null 2>&1; then
            print_status "Keycloak: Running"
        else
            print_error "Keycloak: Not running"
        fi

        # Check Auth Service
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            print_status "Auth Service: Running"
        else
            print_error "Auth Service: Not running"
        fi

        # Check Frontend
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_status "Frontend: Running"
        else
            print_error "Frontend: Not running"
        fi
        ;;
    stop)
        echo "Stopping all services..."
        docker-compose down
        pkill -f "python run.py" 2>/dev/null || true
        pkill -f "npm run dev" 2>/dev/null || true
        print_status "All services stopped"
        ;;
    *)
        echo "Usage: $0 {all|keycloak|backend|frontend|status|stop}"
        echo ""
        echo "Commands:"
        echo "  all       - Setup and configure all services (default)"
        echo "  keycloak  - Start only Keycloak"
        echo "  backend   - Start only Auth Service"
        echo "  frontend  - Start only Frontend"
        echo "  status    - Check status of all services"
        echo "  stop      - Stop all services"
        ;;
esac
