#!/bin/bash

# VoltForge Development Setup Script
set -e

echo "🔧 Setting up VoltForge development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Python 3.11+ is available
if ! python3 --version | grep -E "3\.(11|12)" > /dev/null; then
    echo "❌ Python 3.11+ is required. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
# Development environment configuration
ENVIRONMENT=development
DEBUG=true

# Redis configuration
REDIS_URL=redis://localhost:6379/0

# API configuration
API_HOST=0.0.0.0
API_PORT=8000

# External API keys (optional)
# DIGIKEY_API_KEY=your_key_here
# OCTOPART_API_KEY=your_key_here

# Vector database configuration
VECTOR_DB_PATH=./data/vector_db
DATASHEET_CACHE_PATH=./data/datasheets

# Logging
LOG_LEVEL=INFO
EOF
    echo "📝 Created .env file. Please update with your API keys if needed."
fi

# Start Redis with Docker
echo "🚀 Starting Redis..."
docker run -d --name voltforge-redis -p 6379:6379 redis:7-alpine || echo "Redis container already running"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 3

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/vector_db
mkdir -p data/datasheets

# Run database migrations/setup if needed
echo "🗄️ Setting up database..."
# Add any database setup commands here

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "  1. Start the backend: cd backend && uvicorn main:app --reload"
echo "  2. Open frontend: open frontend/index.html in your browser"
echo "  3. Run tests: pytest backend/tests/"
echo ""
echo "🐳 Or use Docker Compose:"
echo "  docker-compose up --build"
echo ""
echo "📚 Documentation: docs/README.md"