@echo off
chcp 65001 > nul
echo === Kích hoạt Healthcare System ===

echo 0. Dọn dẹp các container cũ để tránh khóa cơ sở dữ liệu...
docker compose down

echo 1. Khởi tạo cơ sở dữ liệu trên PostgreSQL...
python create_databases.py
if %errorlevel% neq 0 (
    echo [LỖI] Không thể tạo cơ sở dữ liệu!
    pause
    exit /b %errorlevel%
)

echo 2. Đang khởi dựng các container Docker và chạy migrations...
docker compose up --build -d
if %errorlevel% neq 0 (
    echo [LỖI] Lỗi khi chạy docker compose!
    pause
    exit /b %errorlevel%
)

echo Đang chờ các dịch vụ hoàn tất chạy migrations (15 giây)...
timeout /t 15 /nobreak > nul

echo 3. Đang nạp dữ liệu mẫu (tiếng Việt)...
python feed_data.py
if %errorlevel% neq 0 (
    echo [LỖI] Không thể nạp dữ liệu mẫu!
    pause
    exit /b %errorlevel%
)

echo === Hệ thống khởi chạy thành công! ===
echo Mở trình duyệt tại: http://localhost:8080/
start http://localhost:8080/

pause
