# 🚀 AI E-Commerce System (Microservices)

Hệ thống E-commerce tích hợp AI, được tái cấu trúc thành kiến trúc **Microservices chuẩn**.

**Stack:** Django + MySQL + Neo4j + SimpleRNN (model_best.h5) + Gemini RAG

---

## 📁 Kiến trúc Microservices

Thay vì 1 app nguyên khối (Monolith), hệ thống được chia thành 5 services độc lập:

```text
ecom/
├── api-gateway/        (Port 8000) ──> Nhận request từ Frontend, proxy tới các service
├── product-service/    (Port 8001) ──> Quản lý sản phẩm (Database: product_db)
├── recommend-service/  (Port 8002) ──> Gợi ý AI (model_best.h5)
├── behavior-service/   (Port 8003) ──> Lưu lịch sử (Database: behavior_db)
├── chat-service/       (Port 8004) ──> Chatbot AI (Neo4j + Gemini)
├── frontend/           (HTML/JS)   ──> Gọi API tới Gateway (:8000)
├── seeds/              (Scripts)   ──> Tạo dữ liệu mẫu
└── docker-compose.yml              ──> MySQL & Neo4j
```

---

## ⚙️ CÀI ĐẶT VÀ CHẠY (Bằng 1 Click)

### Bước 1: Khởi động Database
Mở terminal tại thư mục `ecom/`:
```bash
docker compose up -d
```
*(Lưu ý: Nếu bạn vừa cài lại hệ thống, hãy xoá docker volumes cũ: `docker compose down -v` trước khi up).*

### Bước 2: Cài đặt thư viện Python
Do mỗi service có 1 `requirements.txt` riêng, để nhanh chóng, bạn có thể cài tất cả thư viện dùng chung một lần:
```bash
pip install django djangorestframework django-cors-headers mysqlclient neo4j tensorflow numpy pandas requests google-generativeai python-dotenv
```

### Bước 3: Cấu hình API Key (QUAN TRỌNG)
Mở file `ecom/chat-service/.env` và điền API Key của Gemini vào:
```env
GEMINI_API_KEY=your-actual-api-key-here
```

### Bước 4: Tạo bảng (Migrations)
Chạy lệnh này trong thư mục `ecom/` để migrate cho cả 2 database:
```bash
cd product-service
python manage.py makemigrations products
python manage.py migrate
cd ../behavior-service
python manage.py makemigrations behaviors
python manage.py migrate
cd ..
```

### Bước 5: Seed Data
Tiếp tục ở thư mục `ecom/`, nạp dữ liệu mẫu:
```bash
python seeds/seed_products.py
python seeds/seed_behaviors.py
python seeds/import_neo4j.py
```

### Bước 6: Khởi động toàn bộ Services
Về lại thư mục chứa file `start_all.bat` (Thư mục gốc `aiecom2`), click đúp chuột vào file:
👉 **`start_all.bat`**

File này sẽ mở 5 cửa sổ CMD, tự động chạy 5 server ở 5 Port (8000, 8001, 8002, 8003, 8004).

### Bước 7: Trải nghiệm
Mở file `ecom/frontend/index.html` lên trình duyệt.
Tất cả API call từ Frontend sẽ gọi vào `http://127.0.0.1:8000` (API Gateway) và được gateway chia tải tới đúng microservice.

---

## 🕵️‍♂️ Cách Microservices giao tiếp với nhau

Ví dụ khi bạn click "Gợi ý cho tôi" (Recommend):
1. Frontend gọi `POST 127.0.0.1:8000/api/recommend/` (Gateway)
2. Gateway proxy request sang `127.0.0.1:8002/api/recommend/` (Recommend Service)
3. Recommend Service gọi HTTP GET sang `127.0.0.1:8003/api/behaviors/sequence/...` (Behavior Service) để lấy lịch sử click của bạn.
4. Recommend Service dùng model `model_best.h5` để dự đoán ra các ID: `[2, 5, 8]`.
5. Recommend Service gọi HTTP GET sang `127.0.0.1:8001/api/products/by-ids/` (Product Service) để lấy tên, giá của các sản phẩm `2, 5, 8`.
6. Trả kết quả cuối cùng qua Gateway về Frontend.

Tất cả diễn ra hoàn toàn bằng **HTTP Inter-service communication**.
