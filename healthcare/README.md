# 🏥 Healthcare Microservices System

Hệ thống quản lý bệnh viện theo kiến trúc **Microservices** sử dụng **Django REST Framework**, **Docker Compose**, **Nginx (API Gateway)** và **PostgreSQL** trên máy Host. Kèm theo **Web Dashboard** được xây dựng bằng HTML/CSS/JS thuần.

---

## 📐 Kiến trúc hệ thống

Hệ thống sử dụng **Nginx** làm **API Gateway** để định tuyến các API request, giới hạn tần suất (Rate Limiting), và bảo mật các service bên trong. Các service backend (`patient-service`, `clinical-service`, `billing-service`, `inventory-service`) được cô lập bên trong mạng Docker Network và chỉ có thể truy cập từ bên ngoài thông qua Gateway tại cổng `8080`.

```
                       ┌────────────────────────────────────────────────────────┐
                       │                   Docker Network                       │
                       │                                                        │
     :8080  ┌─────────────────────┐                                             │
   ─────────► API Gateway (Nginx) │                                             │
            └──────────┬──────────┘                                             │
                       │                                                        │
                       │ (Proxy /api/v1/...)                                    │
                       ├──────────────┬──────────────┬──────────────┬───────────┤
                       ▼              ▼              ▼              ▼           │
              ┌──────────────┐┌──────────────┐┌──────────────┐┌──────────────┐  │
              │patient-service││doctor-service││clinical-serv.││billing-serv. │  │
              │ (Port 8000)  ││ (Port 8000)  ││ (Port 8000)  ││ (Port 8000)  │  │
              └──────┬───────┘└──────┬───────┘└──────┬───────┘└──────┬───────┘  │
                     │               │               │               │          │
                     │               │               ▼ (REST)        │          │
                     │               │      ┌──────────────────┐     │          │
                     │               │      │inventory-service │     │          │
                     │               │      │   (Port 8000)    │     │          │
                     │               │      └────────┬─────────┘     │          │
                     │               │               │               │          │
                     └───────────────┼───────────────┼───────────────┘          │
                                     │               │                          │
                                     │               │     ┌────────────────┐   │
                                     │               │     │    Redis       │   │
                                     │               │     │  (Port 6379)   │   │
                                     │               │     └────────────────┘   │
                       └─────────────┼───────────────┼──────────────────────────┘
                                     │               │
                                     ▼               ▼ (host.docker.internal:5432)
                                   ┌──────────────────────────────────────────┐
                                   │           Host PostgreSQL                │
                                   │                                          │
                                   │ - healthcare_patient                     │
                                   │ - healthcare_doctor                      │
                                   │ - healthcare_clinical                    │
                                   │ - healthcare_billing                     │
                                   │ - healthcare_inventory                   │
                                   └──────────────────────────────────────────┘
```

### Luồng nghiệp vụ chính: Kê đơn thuốc

```
Bác sĩ → POST /api/v1/prescriptions/  (thông qua Gateway :8080 -> clinical-service)
              │
              ├──► POST /api/v1/internal/deduct-stock/  (inventory-service)
              │         Trừ tồn kho + ghi StockTransaction
              │         Trả về: [{medicine_name, quantity, unit_price}]
              │
              └──► POST /api/v1/internal/create-bill/   (billing-service)
                        Tạo Bill + BillItems với giá từ inventory
```

---

## ⚙️ Yêu cầu hệ thống

- **Docker Desktop** >= 4.x
- **Docker Compose** >= 2.x
- **Python 3.x** cài sẵn trên máy Host (dành cho script tạo db và gieo dữ liệu mẫu).
- Thư viện Python trên máy Host: `pip install psycopg2-binary` (để chạy các script khởi tạo).
- **PostgreSQL** chạy trên máy Host tại cổng `5432`.
  - Tài khoản mặc định: `postgres` / mật khẩu: `1234` (hoặc thay đổi cấu hình tương ứng trong các file `.env`).

---

## 🚀 Cách setup và chạy tự động (Khuyên dùng)

Hệ thống cung cấp kịch bản khởi chạy tự động hóa hoàn toàn từ đầu đến cuối thông qua một click đúp chuột hoặc một câu lệnh duy nhất.

### Trên Windows
Nhấp đúp chuột vào file **`run.bat`** hoặc chạy từ terminal:
```cmd
run.bat
```

### Trên macOS / Linux / Git Bash
Chạy lệnh cấp quyền thực thi và khởi chạy file **`run.sh`**:
```bash
chmod +x run.sh
./run.sh
```

**Kịch bản tự động sẽ thực hiện:**
1. Tạo 4 database riêng biệt trên PostgreSQL máy Host: `healthcare_patient`, `healthcare_clinical`, `healthcare_billing`, `healthcare_inventory` (thông qua `create_databases.py`).
2. Khởi dựng và build các container qua Docker Compose (`docker compose up --build -d`).
3. Đợi các service chạy hoàn thành migrations cấu trúc bảng.
4. Gieo dữ liệu mẫu tiếng Việt phong phú vào các cơ sở dữ liệu mới tạo (thông qua `feed_data.py`).
5. Tự động mở trình duyệt truy cập dashboard tại địa chỉ **http://localhost:8080**.

---

## ⚙️ Cấu hình chi tiết cơ sở dữ liệu

Mỗi service kết nối tới cơ sở dữ liệu PostgreSQL tương ứng trên máy Host thông qua định danh đặc biệt `host.docker.internal` (đại diện cho localhost của máy Host nhìn từ bên trong Docker container).

| Thư mục Service | Tên cơ sở dữ liệu | Cổng | Người dùng | Mật khẩu |
|---|---|---|---|---|
| `patient-service` | `healthcare_patient` | `5432` | `postgres` | `1234` |
| `doctor-service` | `healthcare_doctor` | `5432` | `postgres` | `1234` |
| `clinical-service` | `healthcare_clinical` | `5432` | `postgres` | `1234` |
| `billing-service` | `healthcare_billing` | `5432` | `postgres` | `1234` |
| `inventory-service` | `healthcare_inventory` | `5432` | `postgres` | `1234` |

*Để thay đổi các giá trị này, bạn chỉ cần sửa đổi file `.env` nằm trong từng thư mục của service tương ứng.*

---

## 🛡️ API Gateway & Bảo mật (Nginx)

Nginx được cấu hình tại cổng `8080` đóng vai trò là API Gateway duy nhất tương tác với bên ngoài.

1. **Che giấu cổng dịch vụ**: Các cổng Backend từ `8001` tới `8005` không còn được expose ra máy host để tránh các truy cập trực tiếp vượt qua kiểm soát.
2. **Rate Limiting (Giới hạn tần suất)**: Giới hạn mỗi IP tối đa **10 requests/giây**, cho phép burst tối đa **20 requests** với cơ chế `nodelay`.
3. **OWASP Security Headers**: Tự động chèn các HTTP headers bảo mật:
   - `X-Frame-Options: SAMEORIGIN` (chống Clickjacking)
   - `X-XSS-Protection: 1; mode=block` (chống Cross-Site Scripting)
   - `X-Content-Type-Options: nosniff` (chống Sniffing mime-type)
   - `Referrer-Policy: no-referrer-when-downgrade` (bảo vệ thông tin referrer)
4. **Hardening**: Giới hạn tối đa kích thước body gửi lên `client_max_body_size 10M` và cấu hình các timeouts tối ưu để ngăn chặn tấn công chậm (slowloris).
5. **Gzip Compression**: Tự động nén dữ liệu dạng text, css, js, json để tối ưu hóa băng thông truyền tải.

---

## 🖥️ Web Dashboard (http://localhost:8080)

Dashboard giao diện đẹp mắt (Dark mode & Glassmorphism) được phục vụ tĩnh qua Nginx định tuyến các API request tương đối về `/api/v1`.

| Trang | Chức năng |
|---|---|
| 📊 **Dashboard** | Tổng quan: số bệnh nhân, bác sĩ, lịch hẹn, hóa đơn, kho thuốc |
| 👥 **Bệnh nhân** | Danh sách bệnh nhân (tự động phân trang), thêm mới, xem chi tiết + lịch hẹn của bệnh nhân |
| 🩺 **Bác sĩ** | Danh sách bác sĩ, thêm mới, xem chi tiết + lịch hẹn của bác sĩ |
| 📅 **Lịch hẹn** | Tạo lịch hẹn mới (lựa chọn bác sĩ trực quan từ dropdown), cập nhật trạng thái |
| 📋 **Đơn thuốc** | Kê đơn (tự động cập nhật giảm số lượng thuốc trong kho và tạo hóa đơn nháp tương ứng) |
| 🧾 **Hóa đơn** | Danh sách hóa đơn, xem chi tiết các khoản, thanh toán trực tiếp |
| 💊 **Kho thuốc** | Quản lý thuốc, nhập/xuất kho thủ công, xem lịch sử giao dịch chi tiết |

---

## 🔌 Kết nối PostgreSQL qua Client (pgAdmin, DBeaver, v.v.)

Bạn có thể kết nối trực tiếp đến PostgreSQL máy host để kiểm tra dữ liệu:

- **Host**: `127.0.0.1` hoặc `localhost`
- **Port**: `5432`
- **User**: `postgres`
- **Password**: `1234`
- **Databases**: `healthcare_patient`, `healthcare_doctor`, `healthcare_clinical`, `healthcare_billing`, `healthcare_inventory`

---

## 📋 Hướng dẫn sử dụng API (Thông qua Gateway :8080)

Do các cổng dịch vụ riêng lẻ đã được ẩn đi, tất cả các yêu cầu API từ bên ngoài đều phải đi qua Gateway tại cổng `8080`.

### 1. Dịch vụ Bệnh nhân (Patient Service)

#### Tạo bệnh nhân mới
```bash
curl -X POST http://localhost:8080/api/v1/patients/ \
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

#### Danh sách / Chi tiết bệnh nhân
```bash
curl http://localhost:8080/api/v1/patients/
curl http://localhost:8080/api/v1/patients/1/
```

#### Xem lịch hẹn của bệnh nhân
```bash
curl http://localhost:8080/api/v1/patients/1/appointments/
```

---

### 5. Dịch vụ Bác sĩ (Doctor Service)

#### Tạo bác sĩ mới
```bash
curl -X POST http://localhost:8080/api/v1/doctors/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Bác sĩ Nguyễn Văn An",
    "specialty": "Tai Mũi Họng",
    "phone": "0911223344",
    "email": "annv@healthcare.com"
  }'
```

#### Danh sách / Chi tiết bác sĩ
```bash
curl http://localhost:8080/api/v1/doctors/
curl http://localhost:8080/api/v1/doctors/1/
```

#### Xem lịch hẹn của bác sĩ
```bash
curl http://localhost:8080/api/v1/doctors/1/appointments/
```

---

### 2. Dịch vụ Lâm sàng (Clinical Service)

#### Tạo lịch hẹn khám
```bash
curl -X POST http://localhost:8080/api/v1/appointments/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "doctor_id": 1,
    "scheduled_at": "2026-12-20T09:00:00",
    "notes": "Khám định kỳ"
  }'
```

#### Cập nhật trạng thái lịch hẹn
```bash
curl -X PATCH http://localhost:8080/api/v1/appointments/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

#### Kê đơn thuốc (Hệ thống tự động trừ kho thuốc & sinh hóa đơn)
```bash
curl -X POST http://localhost:8080/api/v1/prescriptions/ \
  -H "Content-Type: application/json" \
  -d '{
    "appointment": 1,
    "patient_id": 1,
    "diagnosis": "Cảm cúm thông thường, viêm họng nhẹ",
    "items": [
      {"medicine_name": "Paracetamol 500mg", "quantity": 10, "dosage": "2 viên/lần, 3 lần/ngày"},
      {"medicine_name": "Amoxicillin 500mg", "quantity": 6,  "dosage": "1 viên/lần, 3 lần/ngày"}
    ]
  }'
```

---

### 3. Dịch vụ Hóa đơn (Billing Service)

#### Lấy danh sách hóa đơn
```bash
curl http://localhost:8080/api/v1/bills/
```

#### Thanh toán hóa đơn
```bash
curl -X PUT http://localhost:8080/api/v1/bills/1/pay/
```

---

### 4. Dịch vụ Kho thuốc (Inventory Service)

#### Xem danh sách các loại thuốc
```bash
curl http://localhost:8080/api/v1/medicines/
```

#### Nhập kho thêm thuốc
```bash
curl -X PATCH http://localhost:8080/api/v1/medicines/1/stock/ \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100, "transaction_type": "import"}'
```

#### Xem lịch sử các giao dịch kho
```bash
curl http://localhost:8080/api/v1/stock-transactions/
```

---

## 🗂️ Cấu trúc thư mục dự án

```
healthcare/
├── docker-compose.yml        ← Docker Compose khởi chạy 5 service, Redis & API Gateway
├── create_databases.py       ← Khởi tạo 5 database trên PostgreSQL máy Host
├── feed_data.py              ← Script gieo dữ liệu mẫu tiếng Việt đa dạng
├── run.bat                   ← Kịch bản click đúp chuột chạy tự động trên Windows
├── run.sh                    ← Kịch bản chạy tự động trên macOS/Linux/Git Bash
├── .env.example
├── README.md                 ← Tài liệu hướng dẫn sử dụng này
│
├── frontend/                 ← Web Dashboard chạy thông qua Nginx API Gateway
│   ├── nginx.conf            ← Định cấu hình Gateway, Security Headers, Rate limiting, Gzip
│   └── html/                 ← Mã nguồn HTML/CSS/JS tĩnh của frontend
│
├── patient-service/          ← Dịch vụ quản lý thông tin bệnh nhân (Cổng Docker nội bộ: 8000)
├── doctor-service/           ← Dịch vụ quản lý bác sĩ (Cổng Docker nội bộ: 8000)
├── clinical-service/         ← Dịch vụ quản lý lâm sàng, lịch hẹn & kê đơn (Cổng Docker nội bộ: 8000)
├── billing-service/          ← Dịch vụ quản lý hóa đơn & thanh toán (Cổng Docker nội bộ: 8000)
└── inventory-service/        ← Dịch vụ quản lý kho thuốc & nhập xuất (Cổng Docker nội bộ: 8000)
```

---

## 🛠️ Một số lệnh thủ công hữu ích

### Xem logs của một service cụ thể
```bash
docker compose logs -f patient-service
docker compose logs -f api-gateway
```

### Chạy lại migrations thủ công
```bash
docker compose exec patient-service   python manage.py migrate
docker compose exec doctor-service    python manage.py migrate
docker compose exec clinical-service  python manage.py migrate
docker compose exec billing-service   python manage.py migrate
docker compose exec inventory-service python manage.py migrate
```

### Chạy lại script gieo dữ liệu mẫu
```bash
python feed_data.py
```

### Reset toàn bộ hệ thống (xóa các container cũ và dựng lại)
```bash
docker compose down -v
docker compose up --build -d
```
