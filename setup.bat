@echo off
REM Quick setup script for metadata service (Windows)

echo.
echo ========================================
echo Metadata Service - Setup Script (Windows)
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo X Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✓ Docker found

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo X Docker Compose is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

echo ✓ Docker Compose found

REM Copy .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo ✓ .env file created. Please review and update if needed.
) else (
    echo ✓ .env file already exists
)

REM Build and start containers
echo.
echo Building Docker images...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

REM Wait for MySQL to be ready
echo.
echo ⏳ Waiting for MySQL to be ready (10 seconds)...
timeout /t 10 /nobreak

REM Check if API is running
echo.
echo Checking if API is running...

setlocal enabledelayedexpansion
set attempt=0
set max_attempts=30

:wait_loop
if !attempt! geq !max_attempts! (
    echo X API failed to start. Check logs with: docker-compose logs api
    pause
    exit /b 1
)

curl -s http://localhost:8000/health > nul 2>&1
if errorlevel 0 (
    echo ✓ API is running!
    goto done
)

echo ⏳ Waiting for API to start... (!attempt!/!max_attempts!)
timeout /t 2 /nobreak
set /a attempt=!attempt!+1
goto wait_loop

:done
echo.
echo ========================================
echo ✓ Setup Complete!
echo ========================================
echo.
echo Access the API:
echo   - API Base:        http://localhost:8000
echo   - Swagger UI:      http://localhost:8000/docs
echo   - ReDoc:           http://localhost:8000/redoc
echo   - Health Check:    http://localhost:8000/health
echo.
echo Useful Commands:
echo   - View logs:       docker-compose logs -f api
echo   - Stop services:   docker-compose down
echo   - Restart:         docker-compose restart
echo   - Run tests:       docker-compose exec api pytest tests/ -v
echo.
echo Read README.md for detailed documentation
echo.
pause
