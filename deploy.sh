#!/bin/bash

# LLM Deployment Service - Docker Deployment Script
# For Ubuntu Server

set -e  # Exit on any error

echo "🚀 Starting LLM Deployment Service Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
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

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Please run this script from the project directory."
    exit 1
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Remove old images (optional)
print_status "Cleaning up old images..."
docker image prune -f

# Build the new image
print_status "Building Docker image..."
docker-compose build --no-cache

# Start the service
print_status "Starting LLM service..."
docker-compose up -d

# Wait for service to be ready
print_status "Waiting for service to be ready..."
sleep 10

# Check if service is running
if docker-compose ps | grep -q "Up"; then
    print_status "✅ Service is running successfully!"
    
    # Get the container IP
    CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker-compose ps -q))
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================"
    echo "Service URL: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Container IP: $CONTAINER_IP"
    echo ""
    echo "📋 Useful Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop service: docker-compose down"
    echo "  Restart service: docker-compose restart"
    echo "  Check status: docker-compose ps"
    echo ""
    echo "🧪 Test the API:"
    echo "  curl http://localhost:8000/"
    echo ""
    
else
    print_error "❌ Service failed to start. Check logs with: docker-compose logs"
    exit 1
fi
