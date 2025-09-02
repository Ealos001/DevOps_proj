@echo off
REM Sentiment Analysis Project - Stop Script for Windows
REM This script stops all services

echo 🛑 Stopping Sentiment Analysis Project...
echo ========================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running.
    pause
    exit /b 1
)

REM Stop all services
echo 🐳 Stopping all services...
docker-compose down

REM Optional: Remove volumes (uncomment if you want to reset data)
REM echo 🗑️  Removing volumes...
REM docker-compose down -v

echo ✅ All services stopped successfully!
echo ========================================
echo To start again, run: start.bat
echo.
pause



