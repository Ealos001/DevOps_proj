#!/bin/bash

# Sentiment Analysis Project - Startup Script for macOS/Linux
# This script starts all services using Docker Compose

echo "🚀 Starting Sentiment Analysis Project..."
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down

# Start all services
echo "🐳 Starting all services with Docker Compose..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if all services are running
echo "🔍 Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "✅ All services started successfully!"
echo "========================================"
echo "🌐 Web Application:    http://localhost:5000"
echo "📊 Prometheus:         http://localhost:9090"
echo "📈 Grafana:            http://localhost:3000 (admin/admin123)"
echo "🔧 Node Exporter:      http://localhost:9100"
echo ""
echo "📋 Useful commands:"
echo "   View logs:          docker-compose logs -f"
echo "   Stop services:      docker-compose down"
echo "   Restart services:   docker-compose restart"
echo "   Check status:       docker-compose ps"
echo ""
echo "🎯 Next steps:"
echo "   1. Open http://localhost:5000 to test the sentiment analysis"
echo "   2. Configure Jenkins pipeline (see README.md)"
echo "   3. Set up Grafana data source (see README.md)"
echo ""
echo "Happy analyzing! 🎭"
