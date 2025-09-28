@echo off
echo Building and starting services...
docker-compose down
docker-compose build
docker-compose up -d

echo Waiting for services to be healthy...
timeout /t 10 /nobreak

REM Check if database is ready
:check_db
echo Checking database connection...
docker exec taller1-db-1 pg_isready -U postgres 2>nul
if %errorlevel% neq 0 (
    echo Database not ready, waiting...
    timeout /t 2 /nobreak
    goto check_db
)

echo Database is ready! Running seeders...
docker exec taller1-user_service-1 python -m app.seeders.seed

echo Setup complete! Services are running at:
echo - User Service: http://localhost:8000
echo - Mock Main API: http://localhost:8001
echo.
echo API Documentation available at:
echo - Swagger UI: http://localhost:8000/docs
echo - ReDoc: http://localhost:8000/redoc
echo.
echo Press any key to exit...
pause >nul