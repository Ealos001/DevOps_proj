@echo off
REM Sentiment Analysis Project - Startup Script for Windows
REM This script starts all services using Docker Compose

echo 🚀 Starting Sentiment Analysis Project...
echo ========================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker-compose down

REM Start all services
echo 🐳 Starting all services with Docker Compose...
docker-compose up -d

REM Wait for services to start
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if all services are running
echo 🔍 Checking service status...
docker-compose ps

REM Display access information
echo.
echo ✅ All services started successfully!
echo ========================================
echo 🌐 Web Application:    http://localhost:5000
echo 📊 Prometheus:         http://localhost:9090
echo 📈 Grafana:            http://localhost:3000 (admin/admin123)
REM Node Exporter removed
echo 🧰 Jenkins:            http://localhost:8080

REM Verify Jenkins is responding
echo.
echo 🔎 Checking Jenkins readiness...
for /l %%i in (1,1,20) do (
    powershell -Command "try { $resp = (Invoke-WebRequest -Uri 'http://localhost:8080/login' -UseBasicParsing -TimeoutSec 5).StatusCode; if ($resp -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
    if %errorlevel%==0 (
        echo ✅ Jenkins is up.
        goto :after_checks
    ) else (
        echo ⏳ Waiting for Jenkins... (attempt %%i of 20)
        timeout /t 5 /nobreak >nul
    )
)
echo ⚠️ Jenkins did not become ready in time. You can still try: http://localhost:8080

:after_checks
echo.
echo 📋 Useful commands:
echo    View logs:          docker-compose logs -f
echo    Stop services:      docker-compose down
echo    Restart services:   docker-compose restart
echo    Check status:       docker-compose ps
echo.
echo 🎯 Next steps:
echo    1. Open http://localhost:5000 to test the sentiment analysis
echo    2. Configure Jenkins pipeline (see README.md)
echo    3. Set up Grafana data source (see README.md)
echo.
echo Happy analyzing! 🎭
echo.
pause

