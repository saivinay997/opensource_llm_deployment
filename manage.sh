#!/bin/bash

# LLM Deployment Service - Management Script
# For Ubuntu Server

case "$1" in
    "start")
        echo "🚀 Starting LLM service..."
        docker-compose up -d
        echo "✅ Service started. Check logs with: ./manage.sh logs"
        ;;
    "stop")
        echo "🛑 Stopping LLM service..."
        docker-compose down
        echo "✅ Service stopped."
        ;;
    "restart")
        echo "🔄 Restarting LLM service..."
        docker-compose restart
        echo "✅ Service restarted."
        ;;
    "logs")
        echo "📋 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    "status")
        echo "📊 Service status:"
        docker-compose ps
        ;;
    "build")
        echo "🔨 Building Docker image..."
        docker-compose build --no-cache
        echo "✅ Build complete."
        ;;
    "deploy")
        echo "🚀 Full deployment..."
        ./deploy.sh
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        docker-compose down
        docker image prune -f
        docker volume prune -f
        echo "✅ Cleanup complete."
        ;;
    "test")
        echo "🧪 Testing API..."
        curl -s http://localhost:8000/ | jq . 2>/dev/null || curl -s http://localhost:8000/
        ;;
    *)
        echo "LLM Deployment Service - Management Script"
        echo "Usage: $0 {start|stop|restart|logs|status|build|deploy|clean|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  logs    - Show service logs"
        echo "  status  - Show service status"
        echo "  build   - Build Docker image"
        echo "  deploy  - Full deployment (build + start)"
        echo "  clean   - Clean up Docker resources"
        echo "  test    - Test API endpoint"
        exit 1
        ;;
esac
