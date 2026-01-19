# Microservices Django - Book Store Application

## 📋 Tổng quan

Đây là phiên bản **Microservices Architecture** của hệ thống Book Store. Hệ thống được chia thành các services độc lập, mỗi service quản lý một domain riêng biệt với database riêng và giao tiếp qua HTTP REST APIs.

## 🏗️ Microservices Architecture

```
                    ┌──────────────────────┐
                    │   Frontend Gateway   │
                    │    (Port 8000)       │
                    │   User Interface     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
    │ Customer Service│ │ Book Service │ │  Cart Service   │
    │   (Port 8001)   │ │ (Port 8002)  │ │  (Port 8003)    │
    │                 │ │              │ │                 │
    │ - Auth          │ │ - Catalog    │ │ - Shopping Cart │
    │ - Register      │ │ - Stock Mgmt │ │ - Order Items   │
    └────────┬────────┘ └──────┬───────┘ └────────┬────────┘
             │                 │                   │
    ┌────────▼────────┐ ┌──────▼───────┐ ┌────────▼────────┐
    │  Customer DB    │ │   Book DB    │ │    Cart DB      │
    │                 │ │              │ │                 │
    └─────────────────┘ └──────────────┘ └─────────────────┘
```

## 📁 Cấu trúc dự án

```
Microservices Django/
├── .env                        # Shared environment config
├── .gitignore
├── create.sql                  # Database creation for all services
├── README.md                   # This file
│
├── frontend/                   # 🌐 Frontend Gateway Service
│   ├── manage.py
│   ├── requirements.txt
│   ├── frontend_service/      # Django project settings
│   ├── web/                   # Views, URLs
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JS
│
├── customer-service/          # 👤 Customer/Auth Service
│   ├── manage.py
│   ├── requirements.txt
│   ├── customer_service/      # Django project
│   └── customers/             # Django app
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       └── urls.py
│
├── book-service/              # 📚 Book Catalog Service
│   ├── manage.py
│   ├── requirements.txt
│   ├── book_service/          # Django project
│   └── books/                 # Django app
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       └── urls.py
│
└── cart-service/              # 🛒 Shopping Cart Service
    ├── manage.py
    ├── requirements.txt
    ├── cart_service/          # Django project
    └── carts/                 # Django app
        ├── models.py
        ├── views.py
        ├── serializers.py
        └── urls.py
```

## 🎯 Services Overview

### 1. 🌐 Frontend Gateway (Port 8000)
**Trách nhiệm:**
- Cung cấp giao diện người dùng (HTML/CSS/JS)
- Aggregate data từ các microservices
- Handle routing và rendering
- Session management

**Không có database riêng** - Chỉ tương tác với các services khác qua API

**Tech Stack:**
- Django Templates
- Requests library (gọi APIs)
- Static files serving

---

### 2. 👤 Customer Service (Port 8001)
**Trách nhiệm:**
- Quản lý thông tin khách hàng
- Authentication (Register/Login)
- Customer profile management

**Database:** `customer_db`

**API Endpoints:**
- `POST /api/register/` - Đăng ký tài khoản mới
- `POST /api/login/` - Đăng nhập
- `GET /api/customers/<id>/` - Lấy thông tin customer
- `PUT /api/customers/<id>/` - Cập nhật thông tin

**Models:**
- Customer (id, username, email, password, created_at)

---

### 3. 📚 Book Service (Port 8002)
**Trách nhiệm:**
- Quản lý catalog sách
- Quản lý tồn kho (stock)
- Tìm kiếm và lọc sách

**Database:** `book_db`

**API Endpoints:**
- `GET /api/books/` - Danh sách tất cả sách
- `GET /api/books/<id>/` - Chi tiết một sách
- `POST /api/books/` - Thêm sách mới (admin)
- `PATCH /api/books/<id>/stock/` - Cập nhật tồn kho
- `DELETE /api/books/<id>/` - Xóa sách (admin)

**Models:**
- Book (id, title, author, price, stock, description, created_at)

---

### 4. 🛒 Cart Service (Port 8003)
**Trách nhiệm:**
- Quản lý giỏ hàng của khách hàng
- Thêm/xóa items
- Tính toán tổng giá

**Database:** `cart_db`

**API Endpoints:**
- `POST /api/cart/add/` - Thêm sách vào giỏ
- `GET /api/cart/<customer_id>/` - Xem giỏ hàng
- `DELETE /api/cart/items/<id>/` - Xóa item khỏi giỏ
- `PATCH /api/cart/items/<id>/` - Cập nhật số lượng

**Models:**
- CartItem (id, customer_id, book_id, quantity, created_at)

**Note:** Service này lưu `customer_id` và `book_id` nhưng không có foreign keys - đây là pattern của microservices!

## 🗃️ Database Strategy

### Database Per Service Pattern

Mỗi service có database riêng:
```sql
CREATE DATABASE customer_db;
CREATE DATABASE book_db;
CREATE DATABASE cart_db;
```

### Eventual Consistency

- Không có JOIN giữa các databases
- Data được fetch qua API calls
- Trade-off: Consistency vs Availability

### Data Duplication

Cart Service lưu `customer_id` và `book_id` nhưng:
- Không verify foreign key constraint
- Phải call Customer Service để lấy customer info
- Phải call Book Service để lấy book info

## 🚀 Hướng dẫn cài đặt

### Yêu cầu hệ thống

- Python 3.10+
- MySQL Server
- 4 terminal windows (hoặc sử dụng tmux/screen)

### Bước 1: Setup Databases

```bash
mysql -u root -p < create.sql
```

Hoặc tạo thủ công:
```sql
CREATE DATABASE customer_db;
CREATE DATABASE book_db;
CREATE DATABASE cart_db;
```

### Bước 2: Cấu hình Environment

File `.env` (chung cho tất cả services):
```env
# Customer Service
CUSTOMER_DB_NAME=customer_db
CUSTOMER_DB_USER=root
CUSTOMER_DB_PASSWORD=
CUSTOMER_DB_HOST=localhost
CUSTOMER_DB_PORT=3306

# Book Service
BOOK_DB_NAME=book_db
BOOK_DB_USER=root
BOOK_DB_PASSWORD=
BOOK_DB_HOST=localhost
BOOK_DB_PORT=3306

# Cart Service
CART_DB_NAME=cart_db
CART_DB_USER=root
CART_DB_PASSWORD=
CART_DB_HOST=localhost
CART_DB_PORT=3306

# Service URLs
CUSTOMER_SERVICE_URL=http://localhost:8001
BOOK_SERVICE_URL=http://localhost:8002
CART_SERVICE_URL=http://localhost:8003
```

### Bước 3: Cài đặt và chạy từng service

Mở **4 terminal windows** riêng biệt:

#### Terminal 1: Customer Service (Port 8001)

```bash
cd "Microservices Django/customer-service"

# Tạo virtual environment
python -m venv venv
venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Migrate database
python manage.py makemigrations
python manage.py migrate

# Chạy server
python manage.py runserver 8001
```

#### Terminal 2: Book Service (Port 8002)

```bash
cd "Microservices Django/book-service"

# Các bước tương tự
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8002
```

#### Terminal 3: Cart Service (Port 8003)

```bash
cd "Microservices Django/cart-service"

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8003
```

#### Terminal 4: Frontend Gateway (Port 8000)

```bash
cd "Microservices Django/frontend"

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Không cần migrate vì không có database
python manage.py runserver 8000
```

### Bước 4: Kiểm tra services

Mở browser và test:

- Frontend: http://localhost:8000
- Customer API: http://localhost:8001/api/customers/
- Book API: http://localhost:8002/api/books/
- Cart API: http://localhost:8003/api/cart/

## 🔄 Service Communication Flow

### Ví dụ: User thêm sách vào giỏ

```
1. [User Browser]
   ↓ POST request to Frontend
   
2. [Frontend Service :8000]
   ↓ Verify user logged in (session)
   ↓ GET http://localhost:8002/api/books/{book_id}
   
3. [Book Service :8002]
   ↓ Check stock availability
   ↓ Return book info
   
4. [Frontend Service :8000]
   ↓ POST http://localhost:8003/api/cart/add/
   ↓ {customer_id, book_id, quantity}
   
5. [Cart Service :8003]
   ↓ Save to cart_db
   ↓ Return success
   
6. [Frontend Service :8000]
   ↓ Render cart page
   ↓ GET http://localhost:8003/api/cart/{customer_id}
   
7. [Cart Service :8003]
   ↓ Get cart items
   ↓ Return list of {customer_id, book_id, quantity}
   
8. [Frontend Service :8000]
   ↓ For each cart item:
   ↓ GET http://localhost:8002/api/books/{book_id}
   
9. [Book Service :8002]
   ↓ Return book details
   
10. [Frontend Service :8000]
    ↓ Aggregate data
    ↓ Render complete cart with book info
    ↓ Display to user
```

## 📡 API Documentation

### Customer Service API (Port 8001)

#### Register Customer
```http
POST /api/register/
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure123"
}

Response: 201 Created
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

#### Login
```http
POST /api/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure123"
}

Response: 200 OK
{
  "customer_id": 1,
  "username": "john_doe",
  "token": "..."
}
```

### Book Service API (Port 8002)

#### List Books
```http
GET /api/books/

Response: 200 OK
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert Martin",
    "price": "29.99",
    "stock": 10
  }
]
```

#### Update Stock
```http
PATCH /api/books/1/stock/
Content-Type: application/json

{
  "stock": 5
}

Response: 200 OK
```

### Cart Service API (Port 8003)

#### Add to Cart
```http
POST /api/cart/add/
Content-Type: application/json

{
  "customer_id": 1,
  "book_id": 1,
  "quantity": 2
}

Response: 201 Created
```

#### View Cart
```http
GET /api/cart/1/

Response: 200 OK
[
  {
    "id": 1,
    "customer_id": 1,
    "book_id": 1,
    "quantity": 2
  }
]
```

## ✅ Ưu điểm Microservices

- ✅ **Independent Deployment**: Deploy từng service riêng
- ✅ **Scalability**: Scale service có traffic cao
- ✅ **Technology Diversity**: Mỗi service dùng tech khác nhau
- ✅ **Fault Isolation**: Lỗi một service không crash toàn bộ
- ✅ **Team Autonomy**: Nhiều team làm song song
- ✅ **Database Choice**: Mỗi service chọn DB phù hợp

## ❌ Nhược điểm Microservices

- ❌ **Complexity**: Cực kỳ phức tạp
- ❌ **Network Latency**: Nhiều API calls
- ❌ **Data Consistency**: Khó maintain consistency
- ❌ **Debugging**: Khó debug distributed system
- ❌ **Testing**: End-to-end test phức tạp
- ❌ **DevOps**: Cần infrastructure mạnh

## 🧪 Testing

### Unit Testing (từng service)
```bash
cd customer-service
python manage.py test
```

### Integration Testing
```bash
# Test API endpoints
curl http://localhost:8001/api/customers/
curl http://localhost:8002/api/books/
curl http://localhost:8003/api/cart/1/
```

### End-to-End Testing
Sử dụng Postman hoặc automated scripts để test full workflow

## 🐛 Troubleshooting

### Service không kết nối được
```bash
# Check xem service có chạy không
netstat -an | findstr "800"

# Hoặc
curl http://localhost:8001/api/customers/
```

### Database connection error
```bash
# Kiểm tra .env file
# Verify MySQL đang chạy
mysql -u root -p -e "SHOW DATABASES;"
```

### CORS issues (nếu có frontend riêng)
```python
# settings.py của mỗi service
INSTALLED_APPS = [
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True  # Development only!
```

## 📊 So sánh với các kiến trúc khác

| Tiêu chí | Monolithic | Clean Arch | Microservices |
|----------|------------|------------|---------------|
| **Complexity** | Thấp | Trung bình | Rất cao |
| **Scalability** | Khó | Trung bình | Rất tốt |
| **Deployment** | Đơn giản | Đơn giản | Phức tạp |
| **Team Size** | Nhỏ | Trung bình | Lớn |
| **Fault Tolerance** | Thấp | Thấp | Cao |
| **Data Consistency** | Tốt | Tốt | Khó |

## 🛠️ Production Considerations

### Service Discovery
- Sử dụng Consul, Eureka
- Docker Compose với service names

### API Gateway
- Thêm API Gateway layer (Kong, Traefik)
- Handle authentication, rate limiting

### Monitoring
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Prometheus + Grafana
- Distributed tracing (Jaeger)

### Containerization
```dockerfile
# Dockerfile for each service
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Docker Compose
```yaml
version: '3'
services:
  customer-service:
    build: ./customer-service
    ports:
      - "8001:8001"
  book-service:
    build: ./book-service
    ports:
      - "8002:8002"
  # ... other services
```

## 📚 Tài liệu tham khảo

- [Microservices Pattern](https://microservices.io/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Building Microservices by Sam Newman](https://samnewman.io/books/building_microservices/)
- [12 Factor App](https://12factor.net/)

## 📖 Chi tiết từng service

Xem README trong từng folder service để biết chi tiết:
- [Frontend Service README](./frontend/README.md)
- [Customer Service README](./customer-service/README.md)
- [Book Service README](./book-service/README.md)
- [Cart Service README](./cart-service/README.md)

---
**Architecture:** Microservices  
**Services:** 4 (Frontend, Customer, Book, Cart)  
**Communication:** REST APIs  
**Databases:** 3 (MySQL per service)  
**Version:** 3.0
