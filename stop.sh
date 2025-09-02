#!/bin/bash

# Sentiment Analysis Project - Stop Script for macOS/Linux
# This script stops all services

echo "🛑 Stopping Sentiment Analysis Project..."
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running."
    exit 1
fi

# Stop all services
echo "🐳 Stopping all services..."
docker-compose down

# Optional: Remove volumes (uncomment if you want to reset data)
# echo "🗑️  Removing volumes..."
# docker-compose down -v

echo "✅ All services stopped successfully!"
echo "========================================"
echo "To start again, run: ./start.sh"


