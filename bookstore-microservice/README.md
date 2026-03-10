# 📚 Bookstore Microservices

Ứng dụng nhà sách trực tuyến được xây dựng theo kiến trúc **Microservices** sử dụng **Django**, **Django REST Framework** và **Docker Compose**.

---

## 📋 Mục lục

- [Tổng quan kiến trúc](#tổng-quan-kiến-trúc)
- [Danh sách dịch vụ](#danh-sách-dịch-vụ)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt & Chạy dự án](#cài-đặt--chạy-dự-án)
  - [Chạy bằng Docker (Khuyến nghị)](#1-chạy-bằng-docker-khuyến-nghị)
  - [Chạy từng service thủ công](#2-chạy-từng-service-thủ-công)
- [Truy cập ứng dụng](#truy-cập-ứng-dụng)
- [Tài khoản mặc định](#tài-khoản-mặc-định)
- [API Endpoints chi tiết](#api-endpoints-chi-tiết)
- [Data Models](#data-models)
- [Cấu trúc thư mục](#cấu-trúc-thư-mục)
- [Luồng hoạt động](#luồng-hoạt-động)
- [Xử lý sự cố](#xử-lý-sự-cố)

---

## 🏗️ Tổng quan kiến trúc

Sơ đồ kiến trúc chi tiết (từng service) và luồng tổng thể được mô tả bằng Mermaid + PNG trong:

- `docs/architecture/architecture.md`
- `docs/architecture/png/architecture-*.png`

Ở mức đơn giản, mô hình tổng quát là:

```
 Người dùng (Browser) ──HTTP:8000──► API Gateway (Django UI)
                                      │
          ┌───────────────────────────┼────────────────────────────────────────┐
          ▼                           ▼                                        ▼
   Book / Customer / Cart / Order / Review / Pay / Ship / Catalogue / Staff / Manager / Recommender
```

**Nguyên tắc thiết kế:**
- Mỗi service có **database riêng biệt** (SQLite), độc lập hoàn toàn.
- Các service giao tiếp với nhau thông qua **REST API (HTTP)**.
- **API Gateway** là điểm vào duy nhất, xử lý xác thực người dùng và điều phối các request đến service tương ứng.
- Mỗi service được đóng gói trong **Docker container** riêng.

---

## 📦 Danh sách dịch vụ

| Service | Cổng (Host) | Cổng (Container) | Công nghệ | Chức năng |
|---|---|---|---|---|
| **api-gateway** | `8000` | `8000` | Django 5.1 | Cổng vào, xác thực, giao diện web |
| **book-service** | `8002` | `8000` | Django + DRF | Quản lý sách & nhà xuất bản |
| **customer-service** | `8001` | `8000` | Django + DRF | Quản lý khách hàng; auto tạo cart |
| **cart-service** | `8003` | `8000` | Django + DRF | Quản lý giỏ hàng |
| **order-service** | `8004` | `8000` | Django + DRF | Quản lý đơn hàng |
| **review-service** | `8005` | `8000` | Django + DRF | Quản lý đánh giá |
| **ship-service** | `8006` | `8000` | Django + DRF | Quản lý vận chuyển (shipment) |
| **pay-service** | `8007` | `8000` | Django + DRF | Quản lý thanh toán (payment) |
| **catalogue-service** | `8008` | `8000` | Django + DRF | Aggregation sách + rating cho catalogue |
| **staff-service** | `8009` | `8000` | Django + DRF | Hồ sơ nhân viên (staff) |
| **manager-service** | `8010` | `8000` | Django + DRF | Hồ sơ quản lý (manager) |
| **recommender-ai-service** | `8011` | `8000` | Django + DRF | Gợi ý sách dùng Gemini (AI) |

---

## ⚙️ Yêu cầu hệ thống

| Công cụ | Phiên bản tối thiểu | Ghi chú |
|---|---|---|
| **Docker Desktop** | 20.10+ | Bắt buộc khi chạy Docker |
| **Docker Compose** | v2+ | Có sẵn trong Docker Desktop |
| **Python** | 3.11+ | Chỉ cần khi chạy thủ công |
| **pip** | 23+ | Chỉ cần khi chạy thủ công |
| **Node + npm** | Node 18+ | Chỉ cần nếu muốn render lại Mermaid → PNG bằng mermaid-cli |

---

## 🚀 Cài đặt & Chạy dự án

### 1. Chạy bằng Docker (Khuyến nghị)

Đây là cách **nhanh nhất và đơn giản nhất** để khởi động toàn bộ hệ thống.

#### Bước 1 — Clone hoặc tải source code

```bash
# Nếu dùng Git
git clone <repository-url>
cd bookstore-microservice

# Hoặc giải nén thư mục đã tải về
cd bookstore-microservice
```

#### Bước 2 — (Tuỳ chọn) cấu hình Gemini API key cho recommender-ai-service

Nếu bạn muốn bật **recommender-ai-service** dùng Gemini để gợi ý sách:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="YOUR_GEMINI_KEY"

# Linux/macOS (bash/zsh)
export GEMINI_API_KEY="YOUR_GEMINI_KEY"
```

> Nếu **không** đặt `GEMINI_API_KEY`, recommender-ai-service vẫn hoạt động với **fallback** (gợi ý dựa trên rating/stock) nhưng **không gọi Gemini**.

#### Bước 3 — Build và khởi động tất cả services

```bash
docker compose up --build
```

> **Lần đầu chạy:** Docker sẽ pull image Python, cài packages và build các container. Quá trình này mất khoảng **3–5 phút** tùy tốc độ mạng.

> **Lần tiếp theo:** Nếu code không thay đổi, dùng lệnh `docker compose up` để khởi động nhanh hơn (không cần `--build`).

#### Bước 4 — Kiểm tra services đang chạy

```bash
docker compose ps
```

Bạn sẽ thấy 11 container đang ở trạng thái `Up`, ví dụ:

```
NAME                        STATUS     PORTS
bookstore-api-gateway       Up         0.0.0.0:8000->8000/tcp
bookstore-book-service      Up         0.0.0.0:8002->8000/tcp
bookstore-customer-service  Up         0.0.0.0:8001->8000/tcp
bookstore-cart-service      Up         0.0.0.0:8003->8000/tcp
bookstore-order-service     Up         0.0.0.0:8004->8000/tcp
bookstore-review-service    Up         0.0.0.0:8005->8000/tcp
bookstore-ship-service      Up         0.0.0.0:8006->8000/tcp
bookstore-pay-service       Up         0.0.0.0:8007->8000/tcp
bookstore-catalogue-service Up         0.0.0.0:8008->8000/tcp
bookstore-staff-service     Up         0.0.0.0:8009->8000/tcp
bookstore-manager-service   Up         0.0.0.0:8010->8000/tcp
bookstore-recommender-ai    Up         0.0.0.0:8011->8000/tcp
```

#### Bước 5 — Mở ứng dụng

Mở trình duyệt và truy cập: **http://localhost:8000**

#### Dừng và xóa containers

```bash
# Dừng containers (giữ lại data)
docker compose down

# Dừng và xóa cả volumes (reset toàn bộ data)
docker compose down -v
```

#### Xem log của một service cụ thể

```bash
# Xem log API Gateway
docker compose logs api-gateway

# Xem log theo thời gian thực
docker compose logs -f book-service
```

---

### 2. Chạy từng service thủ công

Dùng phương pháp này khi bạn muốn **debug** hoặc **phát triển** một service cụ thể.

> **Lưu ý:** Khi chạy thủ công, các service giao tiếp nội bộ qua hostname Docker (`book-service`, `customer-service`, ...) sẽ không hoạt động. Bạn cần chỉnh sửa URL trong `api-gateway/api_gateway/views.py` thành `localhost`.

#### Cài đặt và chạy từng service

Mở **6 terminal riêng biệt**, mỗi terminal cho một service:

**Terminal 1 — Customer Service**
```bash
cd customer-service
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

**Terminal 2 — Book Service**
```bash
cd book-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

**Terminal 3 — Cart Service**
```bash
cd cart-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8003
```

**Terminal 4 — Order Service**
```bash
cd order-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8004
```

**Terminal 5 — Review Service**
```bash
cd review-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8005
```

**Terminal 6 — API Gateway**
```bash
cd api-gateway
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

---

## 🌐 Truy cập ứng dụng

### Giao diện web (qua API Gateway)

| URL | Mô tả | Quyền truy cập |
|---|---|---|
| http://localhost:8000/ | Trang chủ / Dashboard | Đăng nhập |
| http://localhost:8000/login/ | Đăng nhập | Tất cả |
| http://localhost:8000/register/ | Đăng ký tài khoản | Tất cả |
| http://localhost:8000/books/ | Danh sách sách | Đăng nhập |
| http://localhost:8000/customers/ | Danh sách khách hàng | Admin |
| http://localhost:8000/cart/`<customer_id>`/ | Giỏ hàng | Đăng nhập |
| http://localhost:8000/orders/ | Danh sách đơn hàng | Đăng nhập |
| http://localhost:8000/orders/`<order_id>`/ | Chi tiết đơn hàng | Đăng nhập |
| http://localhost:8000/reviews/ | Đánh giá sách | Đăng nhập |
| http://localhost:8000/admin/ | Trang quản trị Django | Admin |

### REST API trực tiếp từng service

| Service | URL | Endpoints |
|---|---|---|
| Book | http://localhost:8002 | `/books/` |
| Customer | http://localhost:8001 | `/customers/` |
| Cart | http://localhost:8003 | `/carts/...` |
| Order | http://localhost:8004 | `/orders/...` |
| Review | http://localhost:8005 | `/reviews/...` |
| Ship | http://localhost:8006 | `/shipments/...` |
| Pay | http://localhost:8007 | `/payments/...` |

---

## 🔐 Tài khoản mặc định

Khi chạy qua Docker, tài khoản admin được tạo **tự động**:

| Trường | Giá trị |
|---|---|
| **Username** | `admin` |
| **Password** | `admin123` |
| **Email** | `admin@bookstore.com` |
| **Quyền** | Superuser (Admin) |

> ⚠️ **Bảo mật:** Hãy đổi mật khẩu admin trước khi deploy lên môi trường production.

Bạn cũng có thể **tự đăng ký tài khoản** tại http://localhost:8000/register/ — tài khoản thường này sẽ được liên kết với một Customer ID trong customer-service tự động.

---

## 📡 API Endpoints chi tiết

### 📗 Book Service — `http://localhost:8002`

| Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|
| `GET` | `/books/` | Lấy danh sách tất cả sách | — |
| `POST` | `/books/` | Thêm sách mới | `title`, `author`, `price`, `stock` |

**Ví dụ — Thêm sách mới:**
```bash
curl -X POST http://localhost:8002/books/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code", "author": "Robert C. Martin", "price": "299000", "stock": 50}'
```

**Ví dụ — Lấy danh sách sách:**
```bash
curl http://localhost:8002/books/
```

---

### 👥 Customer Service — `http://localhost:8001`

| Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|
| `GET` | `/customers/` | Lấy danh sách khách hàng | — |
| `POST` | `/customers/` | Thêm khách hàng mới | `name`, `email` |

**Ví dụ — Thêm khách hàng:**
```bash
curl -X POST http://localhost:8001/customers/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Nguyễn Văn A", "email": "nguyenvana@email.com"}'
```

---

### 🛒 Cart Service — `http://localhost:8003`

| Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|
| `GET` | `/carts/<customer_id>/` | Lấy giỏ hàng theo customer | — |
| `GET` | `/carts/customer/<customer_id>/` | Lấy thông tin cart object | — |
| `POST` | `/carts/add-item/` | Thêm sách vào giỏ | `cart`, `book_id`, `quantity` |

**Ví dụ — Thêm sách vào giỏ hàng:**
```bash
curl -X POST http://localhost:8003/carts/add-item/ \
  -H "Content-Type: application/json" \
  -d '{"cart": 1, "book_id": 2, "quantity": 3}'
```

---

### 📦 Order Service — `http://localhost:8004`

| Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|
| `GET` | `/orders/` | Lấy tất cả đơn hàng | — |
| `POST` | `/orders/create/` | Tạo đơn hàng mới | `customer_id`, `total_amount`, `items[]` |
| `GET` | `/orders/<order_id>/` | Chi tiết một đơn hàng | — |
| `PATCH` | `/orders/<order_id>/status/` | Cập nhật trạng thái đơn | `status` |
| `GET` | `/orders/customer/<customer_id>/` | Đơn hàng của khách hàng | — |

**Trạng thái đơn hàng:** `pending` → `confirmed` → `shipping` → `delivered` / `cancelled`

**Ví dụ — Tạo đơn hàng:**
```bash
curl -X POST http://localhost:8004/orders/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "total_amount": 598000,
    "items": [
      {"book_id": 1, "quantity": 2, "price_at_order": 299000}
    ]
  }'
```

**Ví dụ — Cập nhật trạng thái:**
```bash
curl -X PATCH http://localhost:8004/orders/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

---

### ⭐ Review Service — `http://localhost:8005`

| Method | Endpoint | Mô tả | Request Body |
|---|---|---|---|
| `GET` | `/reviews/` | Lấy tất cả đánh giá | — |
| `POST` | `/reviews/` | Tạo đánh giá mới | `book_id`, `customer_id`, `customer_name`, `book_title`, `rating`, `comment` |
| `GET` | `/reviews/stats/<book_id>/` | Thống kê rating theo sách | — |

**Ví dụ — Gửi đánh giá:**
```bash
curl -X POST http://localhost:8005/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "book_id": 1,
    "customer_id": 1,
    "customer_name": "Nguyễn Văn A",
    "book_title": "Clean Code",
    "rating": 5,
    "comment": "Sách rất hay, đọc rất hữu ích!"
  }'
```

**Ví dụ — Lấy thống kê rating:**
```bash
curl http://localhost:8005/reviews/stats/1/
# Response: {"avg_rating": 4.5, "total_reviews": 12}
```

---

## 🗄️ Data Models

### Book (book-service)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | Integer (PK) | ID tự động |
| `title` | CharField(255) | Tên sách |
| `author` | CharField(255) | Tên tác giả |
| `price` | Decimal(10,2) | Giá sách |
| `stock` | Integer | Số lượng tồn kho |

### Customer (customer-service)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | Integer (PK) | ID tự động |
| `name` | CharField(255) | Họ tên khách hàng |
| `email` | EmailField (unique) | Địa chỉ email |

### Cart & CartItem (cart-service)

| Trường | Kiểu | Mô tả |
|---|---|---|
| Cart.`id` | Integer (PK) | ID giỏ hàng |
| Cart.`customer_id` | Integer | FK → Customer.id |
| CartItem.`cart` | FK(Cart) | Giỏ hàng |
| CartItem.`book_id` | Integer | FK → Book.id |
| CartItem.`quantity` | Integer | Số lượng |

### Order & OrderItem (order-service)

| Trường | Kiểu | Mô tả |
|---|---|---|
| Order.`id` | Integer (PK) | ID đơn hàng |
| Order.`customer_id` | Integer | FK → Customer.id |
| Order.`status` | CharField | pending/confirmed/shipping/delivered/cancelled |
| Order.`total_amount` | Decimal(12,2) | Tổng tiền |
| Order.`created_at` | DateTimeField | Ngày tạo |
| OrderItem.`order` | FK(Order) | Đơn hàng |
| OrderItem.`book_id` | Integer | FK → Book.id |
| OrderItem.`quantity` | Integer | Số lượng |
| OrderItem.`price_at_order` | Decimal(10,2) | Giá tại thời điểm đặt |

### Review (review-service)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `id` | Integer (PK) | ID đánh giá |
| `book_id` | Integer | FK → Book.id |
| `customer_id` | Integer | FK → Customer.id |
| `customer_name` | CharField(255) | Tên khách hàng |
| `book_title` | CharField(255) | Tên sách |
| `rating` | Integer (1-5) | Điểm đánh giá |
| `comment` | TextField | Nội dung đánh giá |
| `created_at` | DateTimeField | Ngày tạo |

---

## 📁 Cấu trúc thư mục

```
bookstore-microservice/
│
├── docker-compose.yml          ← Cấu hình Docker Compose (toàn hệ thống)
├── README.md
│
├── api-gateway/                ← Cổng vào & Giao diện Web
│   ├── Dockerfile
│   ├── requirements.txt        ← Django, requests
│   ├── manage.py
│   ├── api_gateway/
│   │   ├── settings.py         ← Cấu hình Django
│   │   ├── urls.py             ← Định tuyến toàn bộ URL
│   │   ├── views.py            ← Logic gọi tới các services
│   │   ├── auth_views.py       ← Đăng nhập / Đăng ký / Đăng xuất
│   │   ├── models.py           ← UserProfile (liên kết User ↔ Customer)
│   │   └── context_processors.py
│   └── templates/
│       ├── base.html           ← Layout chính
│       ├── index.html          ← Dashboard Admin
│       ├── user_home.html      ← Dashboard User
│       ├── books.html
│       ├── customers.html
│       ├── cart.html
│       ├── orders.html
│       ├── order_detail.html
│       ├── reviews.html
│       ├── login.html
│       └── register.html
│
├── book-service/               ← REST API quản lý sách
│   ├── Dockerfile
│   ├── requirements.txt        ← Django, DRF, requests
│   ├── manage.py
│   ├── book_service/           ← Config project
│   └── app/                   ← App chính
│       ├── models.py           ← Book model
│       ├── serializers.py
│       └── views.py
│
├── customer-service/           ← REST API quản lý khách hàng
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── customer_service/       ← Config project
│   └── app/
│       ├── models.py           ← Customer model
│       ├── serializers.py
│       └── views.py
│
├── cart-service/               ← REST API quản lý giỏ hàng
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── cart_service/           ← Config project
│   └── app/
│       ├── models.py           ← Cart, CartItem models
│       ├── serializers.py
│       └── views.py
│
├── order-service/              ← REST API quản lý đơn hàng
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── order_service/          ← Config project
│   └── app/
│       ├── models.py           ← Order, OrderItem models
│       ├── serializers.py
│       └── views.py
│
├── review-service/             ← REST API quản lý đánh giá
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── review_service/         ← Config project
│   └── app/
│       ├── models.py           ← Review model
│       ├── serializers.py
│       └── views.py
│
├── ship-service/               ← REST API quản lý vận chuyển
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── ship_service/
│   └── app/
│       ├── models.py           ← Shipment model
│       ├── serializers.py
│       └── views.py
│
├── pay-service/                ← REST API quản lý thanh toán
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── pay_service/
│   └── app/
│       ├── models.py           ← Payment model
│       ├── serializers.py
│       └── views.py
│
└── data/                       ← Thư mục lưu SQLite data (mount volume)
    ├── customer/
    ├── book/
    ├── cart/
    ├── order/
    ├── review/
    ├── ship/
    ├── pay/
    └── gateway/
```

---

## 🔄 Luồng hoạt động

### Luồng đăng ký → mua hàng

```
1. Đăng ký tài khoản (/register/)
   └─ Tạo Django User trong api-gateway DB
   └─ Gọi POST /customers/ → tạo Customer trong customer-service
   └─ Tạo UserProfile liên kết User ↔ customer_id

2. Đăng nhập (/login/)
   └─ Xác thực bằng Django auth

3. Xem sách (/books/)
   └─ API Gateway gọi GET book-service:/books/
   └─ (Kèm rating trung bình từ review-service)

4. Thêm vào giỏ (/cart/<customer_id>/)
   └─ API Gateway gọi POST cart-service:/carts/add-item/

5. Thanh toán (/orders/checkout/<customer_id>/)
   └─ Lấy items từ cart-service
   └─ Tính tổng tiền từ book-service
   └─ Gọi POST order-service:/orders/create/
   └─ Redirect đến trang chi tiết đơn hàng

6. Đánh giá sách (/reviews/)
   └─ Gọi POST review-service:/reviews/
```

### Phân quyền

| Tính năng | Người dùng thường | Admin |
|---|---|---|
| Xem sách | ✅ | ✅ |
| Thêm sách | ❌ | ✅ |
| Xem giỏ hàng | Chỉ của mình | ✅ Tất cả |
| Đặt hàng | ✅ | ✅ |
| Xem đơn hàng | Chỉ của mình | ✅ Tất cả |
| Cập nhật trạng thái đơn | ❌ | ✅ |
| Quản lý khách hàng | ❌ | ✅ |
| Gửi đánh giá | ✅ | ✅ |

---

## 🛠️ Xử lý sự cố

### ❌ Port đã bị chiếm

```
Error: port is already allocated
```

**Giải pháp:** Kiểm tra và dừng ứng dụng đang dùng port đó:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill
```

### ❌ Không kết nối được services

```
Lỗi kết nối book-service: ...
```

**Nguyên nhân:** Service đích chưa khởi động xong.

**Giải pháp:**
```bash
# Kiểm tra trạng thái các container
docker compose ps

# Xem log của service bị lỗi
docker compose logs book-service

# Khởi động lại service cụ thể
docker compose restart book-service
```

### ❌ Database lỗi / Migration failed

```bash
# Truy cập vào container và chạy migrate thủ công
docker compose exec api-gateway python manage.py migrate
docker compose exec book-service python manage.py migrate
```

### ❌ Rebuild lại sau khi thay đổi code

```bash
# Rebuild tất cả
docker compose up --build

# Rebuild một service cụ thể
docker compose up --build book-service
```

### ❌ Xóa toàn bộ và bắt đầu lại

```bash
# Dừng, xóa containers, networks và volumes
docker compose down -v

# Xóa images đã build
docker compose down --rmi local

# Khởi động lại từ đầu
docker compose up --build
```

---

## 🔧 Công nghệ sử dụng

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **Python** | 3.11 | Ngôn ngữ lập trình chính |
| **Django** | 5.1.7 | Web framework |
| **Django REST Framework** | 3.15.2 | Xây dựng REST API |
| **requests** | 2.32.3 | Giao tiếp HTTP giữa services |
| **SQLite** | — | Cơ sở dữ liệu (mỗi service một file) |
| **Docker** | 20.10+ | Containerization |
| **Docker Compose** | v2+ | Orchestration đa container |

---

## 📝 Ghi chú phát triển

- **Môi trường phát triển:** Sử dụng `python manage.py runserver` trong mỗi service riêng lẻ.
- **Môi trường production:** Nên thay `runserver` bằng **Gunicorn** hoặc **uWSGI**, và dùng **Nginx** làm reverse proxy.
- **Database production:** Nên thay SQLite bằng **PostgreSQL** hoặc **MySQL** cho từng service.
- **Service Discovery:** Hiện đang dùng tên hostname Docker cố định. Có thể nâng cấp lên **Consul** hoặc **Kubernetes Service Discovery**.
- **Secret Management:** Không để hardcode secret key và password trong code khi deploy production — dùng biến môi trường `.env`.
