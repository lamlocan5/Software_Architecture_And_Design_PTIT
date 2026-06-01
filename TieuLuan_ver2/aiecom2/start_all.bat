@echo off
echo ========================================================
echo 🚀 KHOI DONG HE THONG MICROSERVICES AI E-COMMERCE
echo ========================================================

echo 1. Dang kiem tra/khoi dong Docker (MySQL + Neo4j)...
cd ecom
docker compose up -d

echo 2. Dang khoi dong cac Microservices...

echo Bật Product Service (Port 8001)...
start "Product Service (8001)" cmd /k "cd product-service && python manage.py runserver 8001"

echo Bật Recommend Service (Port 8002)...
start "Recommend Service (8002)" cmd /k "cd recommend-service && python manage.py runserver 8002"

echo Bật Behavior Service (Port 8003)...
start "Behavior Service (8003)" cmd /k "cd behavior-service && python manage.py runserver 8003"

echo Bật Chat Service (Port 8004)...
start "Chat Service (8004)" cmd /k "cd chat-service && python manage.py runserver 8004"

echo Bật API Gateway (Port 8000)...
start "API Gateway (8000)" cmd /k "cd api-gateway && python manage.py runserver 8000"

echo ========================================================
echo ✅ TAT CA SERVICES DA DUOC KHOI DONG!
echo API Gateway dang chay tai: http://127.0.0.1:8000
echo ========================================================
pause
