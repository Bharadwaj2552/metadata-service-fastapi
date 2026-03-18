#!/bin/bash
# Quick setup script for metadata service

set -e

echo "🚀 Metadata Service - Setup Script"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it first."
    exit 1
fi

echo "✅ Docker Compose found"

# Copy .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update if needed."
else
    echo "✅ .env file already exists"
fi

# Build and start containers
echo "🐳 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 10

# Check if API is running
echo "🔍 Checking if API is running..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API is running!"
        break
    fi
    echo "⏳ Waiting for API to start... ($((attempt + 1))/$max_attempts)"
    sleep 2
    ((attempt++))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API failed to start. Check logs with: docker-compose logs api"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "📚 Access the API:"
echo "   - API Base:        http://localhost:8000"
echo "   - Documentation:   http://localhost:8000/docs"
echo "   - ReDoc:          http://localhost:8000/redoc"
echo "   - Health Check:   http://localhost:8000/health"
echo ""
echo "🛠 Useful Commands:"
echo "   - View logs:      docker-compose logs -f api"
echo "   - Stop services:  docker-compose down"
echo "   - Restart:        docker-compose restart"
echo "   - Run tests:      docker-compose exec api pytest tests/ -v"
echo ""
echo "📖 Read README.md for detailed documentation"
echo ""
