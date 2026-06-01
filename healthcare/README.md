# 🏥 Healthcare Microservices System

Hệ thống quản lý bệnh viện theo kiến trúc **Microservices** sử dụng **Django REST Framework**, **Docker Compose**, và **MySQL**. Kèm theo **Web Dashboard** được xây dựng bằng HTML/CSS/JS thuần.

---

## 📐 Kiến trúc hệ thống

```
                    ┌──────────────────────────────────────────────┐
                    │              Docker Network                  │
                    │                                              │
  :8080  ┌──────────────────┐    ┌──────────────────┐             │
─────────► Frontend (Nginx) │    │                  │             │
         └──────────────────┘    │                  │             │
                                 │                  │             │
  :8001  ┌──────────────────┐    ┌──────────────────┐  :8002      │
─────────► patient-service  │    │ clinical-service ◄─────────────│
         │  db: db_patient  │    │  db: db_clinical │             │
         └──────────────────┘    └────────┬─────────┘             │
                                          │                       │
                                   gọi HTTP (REST)                │
                                    ┌─────┴──────┐                │
                                    ▼            ▼                │
  :8003  ┌──────────────────┐    ┌──────────────────┐  :8004      │
─────────► billing-service  │    │inventory-service ◄─────────────│
         │  db: db_billing  │    │ db: db_inventory │             │
         └──────────────────┘    └──────────────────┘             │
                    │                                             │
                    │  ┌──────────────┐  ┌────────┐              │
                    └──► MySQL :3307  │  │ Redis  │              │
                        │ (host port) │  │  6379  │              │
                        └──────────────┘  └────────┘              │
                    └──────────────────────────────────────────────┘
```

### Luồng nghiệp vụ chính: Kê đơn thuốc

```
Doctor → POST /api/v1/prescriptions/  (clinical-service :8002)
              │
              ├──► POST /api/v1/internal/deduct-stock/  (inventory-service :8004)
              │         Trừ tồn kho + ghi StockTransaction
              │         Trả về: [{medicine_name, quantity, unit_price}]
              │
              └──► POST /api/v1/internal/create-bill/   (billing-service :8003)
                        Tạo Bill + BillItems với giá từ inventory
```

---

## ⚙️ Yêu cầu hệ thống

- **Docker Desktop** >= 4.x
- **Docker Compose** >= 2.x
- **MySQL Workbench** >= 8.0 (optional, để xem database)

---

## 🚀 Cách setup và chạy

### Bước 1: Clone project

```bash
git clone <repository-url>
cd healthcare
```

### Bước 2: Kiểm tra file `.env` (đã có sẵn)

Mỗi service đã có file `.env` với cấu hình mặc định. Mật khẩu MySQL: `123456789`.

| File | DB |
|---|---|
| `patient-service/.env` | `db_patient` |
| `clinical-service/.env` | `db_clinical` |
| `billing-service/.env` | `db_billing` |
| `inventory-service/.env` | `db_inventory` |

### Bước 3: Khởi động toàn bộ hệ thống

```bash
docker compose up --build -d
```

> **Lần đầu build mất 3–5 phút.** Mỗi service sẽ tự động:
> 1. `makemigrations app` — tạo migration files từ models
> 2. `migrate` — áp dụng migration lên MySQL
> 3. `seed_medicines` *(chỉ inventory)* — seed 10 loại thuốc mặc định
> 4. `runserver` — khởi động server

### Bước 4: Kiểm tra trạng thái

```bash
docker compose ps
docker compose logs -f
```

### Bước 5: Mở Dashboard

Truy cập **http://localhost:8080** trên trình duyệt.

---

## 🖥️ Web Dashboard (http://localhost:8080)

Dashboard được xây dựng bằng HTML/CSS/JS thuần, phục vụ qua **Nginx**.

| Trang | Chức năng |
|---|---|
| 📊 **Dashboard** | Tổng quan: số bệnh nhân, lịch hẹn, hóa đơn, kho thuốc |
| 👥 **Bệnh nhân** | Danh sách, thêm mới, xem chi tiết + lịch hẹn |
| 📅 **Lịch hẹn** | Tạo lịch hẹn, cập nhật trạng thái |
| 📋 **Đơn thuốc** | Kê đơn (tự động trừ kho + tạo hóa đơn) |
| 🧾 **Hóa đơn** | Danh sách, xem chi tiết, thanh toán |
| 💊 **Kho thuốc** | Danh sách thuốc, nhập/xuất kho, lịch sử giao dịch |

---

## 🔌 Kết nối MySQL Workbench

> **Lưu ý:** Port host là `3307` (không phải 3306) để tránh xung đột với MySQL local.

| Field    | Value         |
|----------|---------------|
| Host     | `127.0.0.1`   |
| Port     | `3307`        |
| User     | `root`        |
| Password | `123456789`   |

4 databases: `db_patient`, `db_clinical`, `db_billing`, `db_inventory`

---

## 📋 API Documentation

### 1. Patient Service — `http://localhost:8001`

#### Tạo bệnh nhân mới
```bash
curl -X POST http://localhost:8001/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Nguyễn Văn An",
    "date_of_birth": "1990-05-15",
    "gender": "male",
    "phone": "0901234567",
    "email": "nguyenvanan@email.com",
    "address": "123 Đường Láng, Hà Nội"
  }'
```

#### Danh sách / Chi tiết / Xóa bệnh nhân
```bash
curl http://localhost:8001/api/v1/patients/
curl http://localhost:8001/api/v1/patients/1/
curl -X DELETE http://localhost:8001/api/v1/patients/1/
```

#### Xem lịch hẹn của bệnh nhân
```bash
curl http://localhost:8001/api/v1/patients/1/appointments/
```

---

### 2. Clinical Service — `http://localhost:8002`

#### Tạo lịch hẹn
```bash
curl -X POST http://localhost:8002/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_name": "BS. Trần Minh Khoa",
    "scheduled_at": "2024-12-20T09:00:00",
    "notes": "Khám định kỳ"
  }'
```

#### Cập nhật trạng thái lịch hẹn
```bash
curl -X PATCH http://localhost:8002/api/v1/appointments/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
# status: pending | confirmed | completed | cancelled
```

#### Kê đơn thuốc (tự động trừ kho + tạo hóa đơn)
```bash
curl -X POST http://localhost:8002/api/v1/prescriptions/ \
  -H "Content-Type: application/json" \
  -d '{
    "appointment": 1,
    "patient_id": 1,
    "diagnosis": "Cảm cúm thông thường, viêm họng nhẹ",
    "items": [
      {"medicine_name": "Paracetamol 500mg", "quantity": 10, "dosage": "2 viên/lần, 3 lần/ngày"},
      {"medicine_name": "Amoxicillin 500mg", "quantity": 6,  "dosage": "1 viên/lần, 3 lần/ngày"},
      {"medicine_name": "Vitamin C 1000mg",  "quantity": 5,  "dosage": "1 viên/ngày"}
    ]
  }'
```

---

### 3. Billing Service — `http://localhost:8003`

#### Danh sách / Chi tiết hóa đơn
```bash
curl http://localhost:8003/api/v1/bills/
curl http://localhost:8003/api/v1/bills/1/
# Filter theo bệnh nhân:
curl "http://localhost:8003/api/v1/bills/?patient_id=1"
```

#### Thanh toán hóa đơn
```bash
curl -X PUT http://localhost:8003/api/v1/bills/1/pay/
```

---

### 4. Inventory Service — `http://localhost:8004`

#### Danh sách thuốc
```bash
curl http://localhost:8004/api/v1/medicines/
```

#### Thêm thuốc mới
```bash
curl -X POST http://localhost:8004/api/v1/medicines/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cetirizine 10mg",
    "unit": "viên",
    "stock": 200,
    "unit_price": "4500.00"
  }'
```

#### Nhập / Xuất kho thủ công
```bash
# Nhập kho
curl -X PATCH http://localhost:8004/api/v1/medicines/1/stock/ \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100, "transaction_type": "import"}'

# Xuất kho
curl -X PATCH http://localhost:8004/api/v1/medicines/1/stock/ \
  -H "Content-Type: application/json" \
  -d '{"quantity": 10, "transaction_type": "export"}'
```

#### Lịch sử xuất nhập kho
```bash
curl http://localhost:8004/api/v1/stock-transactions/
```

---

## 🔄 Luồng nghiệp vụ đầy đủ (Step-by-step)

```
Bước 1: Tạo bệnh nhân
  POST :8001/api/v1/patients/
  → Patient ID = 1

Bước 2: Đặt lịch hẹn
  POST :8002/api/v1/appointments/  {patient_id: 1, ...}
  → Appointment ID = 1

Bước 3: Xác nhận lịch hẹn
  PATCH :8002/api/v1/appointments/1/  {status: "confirmed"}

Bước 4: Kê đơn thuốc (trigger tự động)
  POST :8002/api/v1/prescriptions/  {appointment: 1, items: [...]}
  → clinical-service gọi:
     ✅ :8004/api/v1/internal/deduct-stock/   ← kho giảm
     ✅ :8003/api/v1/internal/create-bill/    ← hóa đơn nháp được tạo

Bước 5: Kiểm tra hóa đơn
  GET :8003/api/v1/bills/   → thấy bill mới, status="draft"

Bước 6: Thanh toán
  PUT :8003/api/v1/bills/1/pay/
  → status = "paid", paid_at = now()

Bước 7: Kiểm tra kho đã giảm
  GET :8004/api/v1/stock-transactions/  → thấy export transactions
```

---

## 🗂️ Cấu trúc thư mục

```
healthcare/
├── docker-compose.yml        ← MySQL:3307, Redis:6379, 4 services, Frontend:8080
├── init-db.sql               ← Tạo 4 databases tự động
├── .env.example
├── README.md
│
├── frontend/                 ← Web Dashboard (Nginx)
│   ├── nginx.conf
│   └── html/
│       ├── index.html
│       ├── css/style.css     ← Dark mode, glassmorphism
│       └── js/
│           ├── config.js     ← API URLs
│           ├── api.js        ← API wrappers + health check
│           ├── app.js        ← Router, toast, modal
│           ├── dashboard.js
│           ├── patients.js
│           ├── clinical.js   ← Appointments + Prescriptions
│           ├── billing.js
│           └── inventory.js
│
├── patient-service/          ← Port 8001 | DB: db_patient
│   ├── Dockerfile            ← makemigrations → migrate → runserver
│   ├── requirements.txt
│   ├── .env
│   ├── manage.py
│   ├── patient_service/
│   │   ├── settings.py       ← CORS enabled
│   │   └── urls.py
│   └── app/
│       ├── models.py         ← Patient
│       ├── serializers.py    ← Phone validation VN
│       ├── views.py          ← ModelViewSet + appointments action
│       └── urls.py
│
├── clinical-service/         ← Port 8002 | DB: db_clinical
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── models.py         ← Appointment, Prescription, PrescriptionItem
│       ├── views.py          ← Trigger _notify_services() sau khi tạo Prescription
│       └── urls.py
│
├── billing-service/          ← Port 8003 | DB: db_billing
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── models.py         ← Bill, BillItem
│       ├── views.py          ← pay action + internal create-bill endpoint
│       └── urls.py
│
└── inventory-service/        ← Port 8004 | DB: db_inventory
    ├── Dockerfile            ← makemigrations → migrate → seed → runserver
    ├── requirements.txt
    ├── .env
    └── app/
        ├── models.py         ← Medicine, StockTransaction
        ├── views.py          ← stock action + internal deduct-stock endpoint
        ├── urls.py
        └── management/
            └── commands/
                └── seed_medicines.py  ← 10 loại thuốc mặc định
```

---

## 🔐 Internal Service Authentication

Giao tiếp giữa các services dùng header `X-Internal-Key`:
```
X-Internal-Key: super-secret-internal-key-2024
```

Các internal endpoints (không expose ra ngoài):
- `POST :8004/api/v1/internal/deduct-stock/` — trừ kho, trả về unit_price
- `POST :8003/api/v1/internal/create-bill/` — tạo hóa đơn nháp

---

## 🛠️ Troubleshooting

### Xem logs một service cụ thể
```bash
docker compose logs -f inventory-service
docker compose logs -f clinical-service
```

### Migrate thủ công (nếu cần)
```bash
docker compose exec patient-service   python manage.py makemigrations app
docker compose exec patient-service   python manage.py migrate
docker compose exec clinical-service  python manage.py makemigrations app
docker compose exec clinical-service  python manage.py migrate
docker compose exec billing-service   python manage.py makemigrations app
docker compose exec billing-service   python manage.py migrate
docker compose exec inventory-service python manage.py makemigrations app
docker compose exec inventory-service python manage.py migrate
```

### Seed lại dữ liệu thuốc
```bash
docker compose exec inventory-service python manage.py seed_medicines
```

### Reset toàn bộ (xóa data)
```bash
docker compose down -v
docker compose up --build -d
```

### Lỗi port 3306 đã dùng
Port host của MySQL đã được đổi sang **3307** để tránh xung đột với MySQL local. Nếu 3307 cũng bị chiếm, sửa trong `docker-compose.yml`:
```yaml
ports:
  - "3308:3306"   # đổi 3307 thành port khác
```
Và cập nhật kết nối MySQL Workbench tương ứng.

### Lỗi tồn kho không đủ
```bash
# Nhập thêm kho cho thuốc ID=1
curl -X PATCH http://localhost:8004/api/v1/medicines/1/stock/ \
  -H "Content-Type: application/json" \
  -d '{"quantity": 500, "transaction_type": "import"}'
```
