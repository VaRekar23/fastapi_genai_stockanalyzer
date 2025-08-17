@echo off
REM FastAPI GenAI Stock Analyzer - Production Deployment Script for Windows
REM This script automates the deployment process for production environments

echo 🚀 Starting production deployment...

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found! Please create it from .env.example
    pause
    exit /b 1
)

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Stop existing containers if running
echo [INFO] Stopping existing containers...
docker-compose down --remove-orphans

REM Build and start the application
echo [INFO] Building and starting application...
docker-compose up --build -d

REM Wait for application to be ready
echo [INFO] Waiting for application to be ready...
timeout /t 30 /nobreak >nul

REM Check health endpoint
echo [INFO] Checking application health...
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Application is healthy and running!
) else (
    echo ❌ Application health check failed
    echo [INFO] Checking logs...
    docker-compose logs stock-analyzer
    pause
    exit /b 1
)

REM Display deployment information
echo.
echo 🎉 Deployment completed successfully!
echo.
echo 📊 Application Information:
echo    URL: http://localhost:8000
echo    Health Check: http://localhost:8000/health
echo    API Documentation: http://localhost:8000/docs
echo    Alternative Docs: http://localhost:8000/redoc
echo.
echo 🔧 Management Commands:
echo    View logs: docker-compose logs -f stock-analyzer
echo    Stop app: docker-compose down
echo    Restart app: docker-compose restart
echo    Update app: deploy.bat
echo.
echo 📝 Available Endpoints:
echo    GET /stock/{symbol} - Comprehensive stock analysis
echo    GET /intraday/{symbol} - Algorithmic intraday analysis
echo    GET /intraday-agents/{symbol} - AI agent-based intraday analysis
echo    GET /health - Health check
echo    GET /debug/openai - OpenAI configuration check
echo.

echo [INFO] Deployment script completed successfully!
pause
