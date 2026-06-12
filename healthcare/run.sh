#!/bin/bash
echo "=== Kích hoạt Healthcare System ==="

echo "0. Dọn dẹp các container cũ để tránh khóa cơ sở dữ liệu..."
docker compose down

echo "1. Khởi tạo cơ sở dữ liệu trên PostgreSQL..."
python3 create_databases.py
if [ $? -ne 0 ]; then
    echo "[LỖI] Không thể tạo cơ sở dữ liệu!"
    exit 1
fi

echo "2. Đang khởi dựng các container Docker và chạy migrations..."
docker compose up --build -d
if [ $? -ne 0 ]; then
    echo "[LỖI] Lỗi khi chạy docker compose!"
    exit 1
fi

echo "Đang chờ các dịch vụ hoàn tất chạy migrations (15 giây)..."
sleep 15

echo "3. Đang nạp dữ liệu mẫu (tiếng Việt)..."
python3 feed_data.py
if [ $? -ne 0 ]; then
    echo "[LỖI] Không thể nạp dữ liệu mẫu!"
    exit 1
fi

echo "=== Hệ thống khởi chạy thành công! ==="
echo "Mở trình duyệt tại: http://localhost:8080/"

# Open browser based on OS
if [ "$(uname)" == "Darwin" ]; then
    open http://localhost:8080/
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    xdg-open http://localhost:8080/
fi
