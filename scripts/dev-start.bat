@echo off
REM VoltForge Development Setup Script for Windows
setlocal enabledelayedexpansion

echo 🔧 Setting up VoltForge development environment...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if Python 3.11+ is available
python --version | findstr /R "3\.(11\|12)" >nul
if errorlevel 1 (
    echo ❌ Python 3.11+ is required. Please install Python 3.11 or higher.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -e ".[dev]"

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating .env file...
    (
        echo # Development environment configuration
        echo ENVIRONMENT=development
        echo DEBUG=true
        echo.
        echo # Redis configuration
        echo REDIS_URL=redis://localhost:6379/0
        echo.
        echo # API configuration
        echo API_HOST=0.0.0.0
        echo API_PORT=8000
        echo.
        echo # External API keys ^(optional^)
        echo # DIGIKEY_API_KEY=your_key_here
        echo # OCTOPART_API_KEY=your_key_here
        echo.
        echo # Vector database configuration
        echo VECTOR_DB_PATH=./data/vector_db
        echo DATASHEET_CACHE_PATH=./data/datasheets
        echo.
        echo # Logging
        echo LOG_LEVEL=INFO
    ) > .env
    echo 📝 Created .env file. Please update with your API keys if needed.
)

REM Start Redis with Docker
echo 🚀 Starting Redis...
docker run -d --name voltforge-redis -p 6379:6379 redis:7-alpine 2>nul || echo Redis container already running

REM Wait for Redis to be ready
echo ⏳ Waiting for Redis to be ready...
timeout /t 3 /nobreak >nul

REM Create data directories
echo 📁 Creating data directories...
if not exist "data\vector_db" mkdir data\vector_db
if not exist "data\datasheets" mkdir data\datasheets

echo ✅ Development environment setup complete!
echo.
echo 🎯 Next steps:
echo   1. Start the backend: cd backend ^&^& uvicorn main:app --reload
echo   2. Open frontend: open frontend/index.html in your browser
echo   3. Run tests: pytest backend/tests/
echo.
echo 🐳 Or use Docker Compose:
echo   docker-compose up --build
echo.
echo 📚 Documentation: docs/README.md

pause