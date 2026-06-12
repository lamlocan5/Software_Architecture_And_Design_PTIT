@echo off
chcp 65001 > nul
echo =====================================================
echo    Bookstore Microservices - Auto Startup Script
echo =====================================================
echo.

REM Step 1: Check Docker is running
echo [1/4] Checking Docker status...
docker info > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Docker might not be running or is not responding.
    echo Trying to proceed anyway...
) else (
    echo [OK] Docker is running.
)
echo.

REM Step 2: Create databases on PostgreSQL and MySQL
echo [2/4] Creating databases on PostgreSQL and MySQL...
python create_databases.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create databases!
    echo Make sure PostgreSQL on port 5432 and MySQL on port 3306 are running.
    echo Check your .env file for correct DB credentials.
    pause
    exit /b 1
)
echo [OK] Databases ready.
echo.

REM Step 3: Build and start Docker containers in background
echo [3/4] Building and starting Docker containers (background mode)...
docker compose up --build -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker Compose!
    echo Run "docker compose logs" to see error details.
    pause
    exit /b 1
)
echo [OK] All containers started.
echo.

REM Wait for services to initialize and run Django migrations
echo Waiting 20 seconds for services to initialize and run migrations...
ping 127.0.0.1 -n 21 > nul
echo.

REM Step 4: Feed Vietnamese sample data
echo [4/4] Feeding mock data (Vietnamese sample data)...
python feed_data.py
if %errorlevel% neq 0 (
    echo [WARNING] Failed to feed mock data.
    echo You can run "python feed_data.py" manually later.
    echo The system is still running at http://localhost:8000
) else (
    echo [OK] Sample data loaded successfully.
)
echo.

REM Done
echo =====================================================
echo    System started successfully!
echo =====================================================
echo.
echo  Access the application : http://localhost:8000
echo.
echo  Default admin account:
echo    Username : admin
echo    Password : admin123
echo.
echo  Running services:
echo    nginx-gateway            : http://localhost:8000  (main entry)
echo    user-service             : http://localhost:8001
echo    product-service          : http://localhost:8002
echo    cart-service             : http://localhost:8003
echo    order-service            : http://localhost:8004
echo    review-service           : http://localhost:8005
echo    shipping-service         : http://localhost:8006
echo    payment-service          : http://localhost:8007
echo    catalogue-service        : http://localhost:8008
echo    notification-service     : http://localhost:8009
echo    ai-service               : http://localhost:8011

echo.
echo  Useful commands:
echo    docker compose ps          - Check container status
echo    docker compose logs -f     - View live logs
echo    docker compose down        - Stop all containers
echo    docker compose down -v     - Stop and remove all data
echo.

start http://localhost:8000
pause
