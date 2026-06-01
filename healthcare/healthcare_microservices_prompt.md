# 🏥 AI Coding Prompt: Healthcare Microservices System (Django + Docker + MySQL)

## Mục tiêu
Xây dựng một hệ thống quản lý bệnh viện theo kiến trúc **Microservices** sử dụng **Django REST Framework**, **Docker Compose**, và **MySQL** (MySQL Workbench compatible). Hệ thống gồm 4 services độc lập giao tiếp với nhau qua **REST API** và **Event-driven (message queue)**.

---

## 📐 Kiến trúc tổng quan

```
healthcare-system/
├── docker-compose.yml
├── .env.example
├── README.md
│
├── patient-service/          # Quản lý thông tin bệnh nhân
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── patient_service/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── app/
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       └── migrations/
│
├── clinical-service/         # Quản lý khám bệnh & kê đơn
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── clinical_service/
│   └── app/
│
├── billing-service/          # Quản lý hóa đơn & thanh toán
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── billing_service/
│   └── app/
│
└── inventory-service/        # Quản lý kho thuốc
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    ├── inventory_service/
    └── app/
```

---

## 🔧 Yêu cầu kỹ thuật

### Stack
- **Framework**: Django 4.2 + Django REST Framework 3.14
- **Database**: MySQL 8.0 (mỗi service có 1 database riêng biệt — Database per Service pattern)
- **Container**: Docker + Docker Compose
- **Message Queue**: Redis (dùng Django signals + celery để giả lập event-driven đơn giản)
- **Python**: 3.11+

### Packages chung cho mỗi service (`requirements.txt`)
```
Django==4.2
djangorestframework==3.14
mysqlclient==2.2.0
celery==5.3
redis==5.0
django-environ==0.11
requests==2.31
```

---

## 🗄️ Database Schema (MySQL)

### patient-service → DB: `db_patient`

```sql
CREATE TABLE patients (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender      ENUM('male', 'female', 'other') NOT NULL,
    phone       VARCHAR(20) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE,
    address     TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### clinical-service → DB: `db_clinical`

```sql
CREATE TABLE appointments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,   -- FK tới patient-service (logical, không physical)
    doctor_name     VARCHAR(255) NOT NULL,
    scheduled_at    DATETIME NOT NULL,
    status          ENUM('pending','confirmed','completed','cancelled') DEFAULT 'pending',
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prescriptions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id  INT NOT NULL,
    patient_id      INT NOT NULL,
    diagnosis       TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prescription_items (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine_name   VARCHAR(255) NOT NULL,
    quantity        INT NOT NULL,
    dosage          VARCHAR(255),
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
);
```

### billing-service → DB: `db_billing`

```sql
CREATE TABLE bills (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    prescription_id INT,            -- từ clinical-service
    total_amount    DECIMAL(12,2) DEFAULT 0,
    status          ENUM('draft','pending','paid','cancelled') DEFAULT 'draft',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    paid_at         DATETIME
);

CREATE TABLE bill_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    bill_id     INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    unit_price  DECIMAL(12,2) NOT NULL,
    quantity    INT NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id)
);
```

### inventory-service → DB: `db_inventory`

```sql
CREATE TABLE medicines (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) UNIQUE NOT NULL,
    unit        VARCHAR(50) NOT NULL,   -- viên, chai, ống...
    stock       INT DEFAULT 0,
    unit_price  DECIMAL(12,2) NOT NULL,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE stock_transactions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    medicine_id     INT NOT NULL,
    transaction_type ENUM('import','export') NOT NULL,
    quantity        INT NOT NULL,
    reference_id    VARCHAR(255),       -- prescription_id từ clinical-service
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);
```

---

## 🌐 API Endpoints

### Patient Service (port 8001)
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/v1/patients/` | Tạo bệnh nhân mới |
| GET | `/api/v1/patients/` | Danh sách bệnh nhân |
| GET | `/api/v1/patients/{id}/` | Chi tiết bệnh nhân |
| PUT | `/api/v1/patients/{id}/` | Cập nhật thông tin |
| DELETE | `/api/v1/patients/{id}/` | Xóa bệnh nhân |

### Clinical Service (port 8002)
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/v1/appointments/` | Tạo lịch hẹn |
| GET | `/api/v1/appointments/` | Danh sách lịch hẹn |
| PATCH | `/api/v1/appointments/{id}/` | Cập nhật trạng thái |
| POST | `/api/v1/prescriptions/` | Tạo đơn thuốc (trigger event) |
| GET | `/api/v1/prescriptions/{id}/` | Chi tiết đơn thuốc |

### Billing Service (port 8003)
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/v1/bills/` | Danh sách hóa đơn |
| GET | `/api/v1/bills/{id}/` | Chi tiết hóa đơn |
| PUT | `/api/v1/bills/{id}/pay/` | Thanh toán hóa đơn |

### Inventory Service (port 8004)
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/v1/medicines/` | Danh sách thuốc |
| POST | `/api/v1/medicines/` | Thêm thuốc mới |
| PATCH | `/api/v1/medicines/{id}/stock/` | Cập nhật tồn kho |
| GET | `/api/v1/stock-transactions/` | Lịch sử xuất nhập kho |

---

## ⚡ Event-driven Communication

### Luồng chính: Kê đơn thuốc

```
Doctor tạo Prescription (clinical-service)
    │
    ▼
clinical-service gửi HTTP request tới:
    ├── inventory-service: POST /api/v1/internal/deduct-stock/
    │       payload: { prescription_id, items: [{medicine_name, quantity}] }
    │
    └── billing-service: POST /api/v1/internal/create-bill/
            payload: { patient_id, prescription_id, items: [...] }
```

### Internal endpoints (không expose ra ngoài, chỉ service-to-service)
- `POST /api/v1/internal/deduct-stock/` — inventory-service trừ kho
- `POST /api/v1/internal/create-bill/` — billing-service tạo hóa đơn nháp

> **Ghi chú**: Dùng environment variable `INTERNAL_SERVICE_KEY` để xác thực giữa các services (simple header-based auth).

---

## 🐳 Docker Configuration

### `docker-compose.yml` (đầy đủ)

```yaml
version: '3.9'

services:
  # ─── Databases ───────────────────────────────────────────
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # ─── Services ────────────────────────────────────────────
  patient-service:
    build: ./patient-service
    ports:
      - "8001:8000"
    env_file: ./patient-service/.env
    depends_on:
      mysql:
        condition: service_healthy

  clinical-service:
    build: ./clinical-service
    ports:
      - "8002:8000"
    env_file: ./clinical-service/.env
    depends_on:
      mysql:
        condition: service_healthy

  billing-service:
    build: ./billing-service
    ports:
      - "8003:8000"
    env_file: ./billing-service/.env
    depends_on:
      mysql:
        condition: service_healthy

  inventory-service:
    build: ./inventory-service
    ports:
      - "8004:8000"
    env_file: ./inventory-service/.env
    depends_on:
      mysql:
        condition: service_healthy

volumes:
  mysql_data:
```

### `init-db.sql` (tạo 4 databases cùng lúc)

```sql
CREATE DATABASE IF NOT EXISTS db_patient CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_clinical CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_billing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS db_inventory CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON db_patient.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_clinical.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_billing.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON db_inventory.* TO 'root'@'%';
FLUSH PRIVILEGES;
```

### `Dockerfile` (dùng chung cho cả 4 services)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
```

### `.env` mẫu cho mỗi service

```env
# patient-service/.env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=db_patient
DB_USER=root
DB_PASSWORD=rootpassword
DB_HOST=mysql
DB_PORT=3306
INTERNAL_SERVICE_KEY=super-secret-internal-key-2024

# Service URLs (dùng trong clinical-service)
PATIENT_SERVICE_URL=http://patient-service:8000
BILLING_SERVICE_URL=http://billing-service:8000
INVENTORY_SERVICE_URL=http://inventory-service:8000
```

---

## ⚙️ Django Settings quan trọng

```python
# settings.py — áp dụng cho tất cả services
import environ
env = environ.Env()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

---

## 📋 Yêu cầu code chi tiết

### 1. Patient Service
- Model `Patient` đầy đủ các fields đã định nghĩa ở trên
- CRUD ViewSet với DRF `ModelViewSet`
- Serializer với validation: phone phải đúng định dạng VN, email optional
- Custom action: `GET /api/v1/patients/{id}/appointments/` — gọi sang clinical-service lấy lịch hẹn

### 2. Clinical Service
- Model `Appointment` + `Prescription` + `PrescriptionItem`
- Khi tạo Prescription thành công → gọi `_notify_services()`:
  - Gọi `inventory-service` để trừ kho
  - Gọi `billing-service` để tạo hóa đơn nháp
- Nếu một service lỗi → log warning, không rollback (best-effort)
- Endpoint lấy thông tin bệnh nhân: gọi sang patient-service, cache kết quả 60s

### 3. Billing Service
- Model `Bill` + `BillItem`
- Internal endpoint `POST /api/v1/internal/create-bill/` nhận data từ clinical-service
- Action `PUT /api/v1/bills/{id}/pay/`: đổi status thành 'paid', lưu paid_at
- Tính tổng tiền tự động từ BillItems

### 4. Inventory Service
- Model `Medicine` + `StockTransaction`
- Internal endpoint `POST /api/v1/internal/deduct-stock/`: trừ kho + ghi transaction
- Trả về lỗi nếu tồn kho không đủ (HTTP 400)
- Seed data: 10 loại thuốc phổ biến

---

## 📝 README.md yêu cầu

File `README.md` ở root phải có đầy đủ các mục:

```markdown
# Healthcare Microservices System

## Giới thiệu dự án
...mô tả kiến trúc, sơ đồ ASCII của các services...

## Kiến trúc hệ thống
[sơ đồ services và cách giao tiếp]

## Yêu cầu hệ thống
- Docker Desktop >= 4.x
- Docker Compose >= 2.x
- MySQL Workbench >= 8.0 (optional, để xem database)

## Cách setup và chạy

### Bước 1: Clone project
### Bước 2: Copy và cấu hình .env
### Bước 3: Khởi động toàn bộ hệ thống
### Bước 4: Chạy migrations
### Bước 5: Load seed data

## Kết nối MySQL Workbench
Host: 127.0.0.1 | Port: 3306 | User: root | Password: rootpassword

## API Documentation
[liệt kê tất cả endpoints với ví dụ curl]

## Luồng nghiệp vụ chính
[Mô tả step-by-step từ tạo bệnh nhân → đặt lịch → kê đơn → thanh toán]

## Cấu trúc thư mục
## Troubleshooting
```

---

## ✅ Checklist output AI cần hoàn thành

- [ ] Toàn bộ cấu trúc thư mục như trên
- [ ] `docker-compose.yml` + `init-db.sql` đầy đủ
- [ ] 4 Django services độc lập, mỗi service có Dockerfile + requirements.txt + .env.example
- [ ] Models, Serializers, Views, URLs cho từng service
- [ ] Internal service-to-service communication hoạt động
- [ ] Seed data cho inventory (10 loại thuốc)
- [ ] README.md chi tiết với hướng dẫn setup từng bước
- [ ] Test manual bằng curl commands trong README

---

## 💡 Lưu ý cho AI

1. **Không dùng SQLite** — bắt buộc MySQL cho tất cả services
2. **Database per Service** — mỗi service kết nối 1 database riêng, không share
3. **Không dùng API Gateway** ở bước này — gọi thẳng port từng service
4. **Error handling**: wrap tất cả service-to-service calls trong try/except, log lỗi, trả về response phù hợp
5. **Đặt tên database**: `db_patient`, `db_clinical`, `db_billing`, `db_inventory`
6. **Port mapping**: patient=8001, clinical=8002, billing=8003, inventory=8004
7. **Migrations**: mỗi service tự chạy `migrate` khi container start
