@echo off
echo ===========================================
echo === Start Healthcare Microservices System ===
echo ===========================================

echo 1. Cleaning up old containers...
docker compose down --remove-orphans


echo 2. Initializing PostgreSQL databases...
python create_databases.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create databases!
    pause
    exit /b 1
)

echo 3. Building and launching Docker containers...
docker compose up --build -d
if %errorlevel% neq 0 (
    echo [ERROR] Docker compose build/up failed!
    pause
    exit /b 1
)

echo Waiting for services migrations to complete (15 seconds)...
ping 127.0.0.1 -n 16 > nul

echo 4. Seeding mock data...
python feed_data.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to seed mock data!
    pause
    exit /b 1
)

echo === System started successfully! ===
echo Open browser at: http://localhost:8080/
start http://localhost:8080/

pause
