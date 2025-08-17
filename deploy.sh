#!/bin/bash

# FastAPI GenAI Stock Analyzer - Production Deployment Script
# This script automates the deployment process for production environments

set -e  # Exit on any error

echo "🚀 Starting production deployment..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found! Please create it from .env.example"
    exit 1
fi

# Check if required environment variables are set
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    print_error "OPENAI_API_KEY not set in .env file"
    exit 1
fi

print_status "Environment variables validated"

# Create logs directory if it doesn't exist
mkdir -p logs

# Stop existing containers if running
print_status "Stopping existing containers..."
docker-compose down --remove-orphans || true

# Build and start the application
print_status "Building and starting application..."
docker-compose up --build -d

# Wait for application to be ready
print_status "Waiting for application to be ready..."
sleep 30

# Check health endpoint
print_status "Checking application health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "✅ Application is healthy and running!"
else
    print_error "❌ Application health check failed"
    print_status "Checking logs..."
    docker-compose logs stock-analyzer
    exit 1
fi

# Display deployment information
echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Application Information:"
echo "   URL: http://localhost:8000"
echo "   Health Check: http://localhost:8000/health"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Alternative Docs: http://localhost:8000/redoc"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose logs -f stock-analyzer"
echo "   Stop app: docker-compose down"
echo "   Restart app: docker-compose restart"
echo "   Update app: ./deploy.sh"
echo ""
echo "📝 Available Endpoints:"
echo "   GET /stock/{symbol} - Comprehensive stock analysis"
echo "   GET /intraday/{symbol} - Algorithmic intraday analysis"
echo "   GET /intraday-agents/{symbol} - AI agent-based intraday analysis"
echo "   GET /health - Health check"
echo "   GET /debug/openai - OpenAI configuration check"
echo ""

print_status "Deployment script completed successfully!"
