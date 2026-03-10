# 📚 BookStore Microservices

Hệ thống quản lý sách theo kiến trúc Microservices với Django REST Framework.

## 🗂️ Cấu trúc dự án

```
bookstore_micro05/
├── customer-service/   # Quản lý khách hàng (port 8001)
├── book-service/       # Quản lý sách (port 8002)
├── cart-service/       # Quản lý giỏ hàng (port 8003)
├── api_gateway/        # API Gateway - giao diện người dùng (port 8000)
└── docker-compose.yml
```

---

## 🚀 Cách chạy (Không dùng Docker)

Cần mở **4 terminal** riêng biệt, chạy theo thứ tự:

---

### Terminal 1 — customer-service

```bash
cd c:\bookstore_micro05\customer-service
venv\Scripts\activate
pip install django djangorestframework requests
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8001
```

---

### Terminal 2 — book-service

```bash
cd c:\bookstore_micro05\book-service
venv\Scripts\activate
pip install django djangorestframework requests
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8002
```

---

### Terminal 3 — cart-service

```bash
cd c:\bookstore_micro05\cart-service
venv\Scripts\activate
pip install django djangorestframework requests
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8003
```

---

### Terminal 4 — api-gateway

```bash
cd c:\bookstore_micro05\api_gateway
pip install django requests
python manage.py migrate
python manage.py runserver 8000
```

> **Lưu ý:** Nếu chưa có `venv` trong service nào, tạo trước:
> ```bash
> python -m venv venv
> venv\Scripts\activate
> ```

---

## 🌐 Truy cập ứng dụng

Mở trình duyệt và vào:

| Trang | URL |
|-------|-----|
| 📖 Danh sách sách | http://127.0.0.1:8000/books/ |
| 🛒 Giỏ hàng | http://127.0.0.1:8000/cart/1/ |
| ⚙️ Admin | http://127.0.0.1:8000/admin/ |

---

## 🐳 Cách chạy bằng Docker (cần cài Docker Desktop)

```bash
cd c:\bookstore_micro05
docker compose up --build
```

Sau khi Docker chạy xong, mở trình duyệt vào các link sau:

| Service | URL | Mô tả |
|---------|-----|-------|
| 🏠 API Gateway | [http://localhost:8000/books/](http://localhost:8000/books/) | Trang chính - danh sách sách |
| 🛒 Giỏ hàng | [http://localhost:8000/cart/1/](http://localhost:8000/cart/1/) | Xem giỏ hàng khách hàng #1 |
| ⚙️ Admin Gateway | [http://localhost:8000/admin/](http://localhost:8000/admin/) | Trang quản trị Gateway |
| 📗 Book Service | [http://localhost:8002/books/](http://localhost:8002/books/) | API danh sách sách (trực tiếp) |
| 👤 Customer Service | [http://localhost:8001/customers/](http://localhost:8001/customers/) | API danh sách khách hàng (trực tiếp) |
| 🛍️ Cart Service | [http://localhost:8003/carts/](http://localhost:8003/carts/) | API giỏ hàng (trực tiếp) |

Tải Docker Desktop tại: https://www.docker.com/products/docker-desktop

---

## 📡 API Endpoints

### book-service (port 8002)
| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/books/` | Lấy danh sách sách |
| POST | `/books/` | Thêm sách mới |

**Thêm sách mới (POST):**
```json
{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "price": "29.99",
    "stock": 10
}
```

### cart-service (port 8003)
| Method | URL | Mô tả |
|--------|-----|-------|
| POST | `/carts/` | Tạo giỏ hàng |
| POST | `/carts/add-item/` | Thêm sách vào giỏ |
| GET | `/carts/<customer_id>/` | Xem giỏ hàng |

**Tạo giỏ hàng (POST `/carts/`):**
```json
{
    "customer_id": 1
}
```

**Thêm item (POST `/carts/add-item/`):**
```json
{
    "cart": 1,
    "book_id": 1,
    "quantity": 2
}
```

### customer-service (port 8001)
| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/customers/` | Lấy danh sách khách hàng |
| POST | `/customers/` | Tạo khách hàng mới |

**Tạo khách hàng mới (POST `/customers/`):**
```json
{
    "name": "Nguyen Van A",
    "email": "a@example.com",
    "password": "123456"
}
```

---

## 🧪 Hướng dẫn sử dụng từng bước

Sau khi Docker chạy, làm theo thứ tự sau:

### Bước 1 — Thêm sách (`book-service`)

Vào [http://localhost:8002/books/](http://localhost:8002/books/), nhập vào ô **Content** rồi bấm **POST**:

```json
{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "price": "29.99",
    "stock": 10
}
```

> Bấm **GET** để kiểm tra sách đã được thêm (xuất hiện trong danh sách `[{...}]`)

---

### Bước 2 — Tạo khách hàng (`customer-service`)

Vào [http://localhost:8001/customers/](http://localhost:8001/customers/), nhập vào ô **Content** rồi bấm **POST**:

```json
{
    "name": "Nguyen Van A",
    "email": "a@example.com",
    "password": "123456"
}
```

> Ghi nhớ `id` của customer trả về (thường là `1`)

---

### Bước 3 — Tạo giỏ hàng (`cart-service`)

Vào [http://localhost:8003/carts/](http://localhost:8003/carts/), nhập vào ô **Content** rồi bấm **POST**:

```json
{
    "customer_id": 1
}
```

---

### Bước 4 — Thêm sách vào giỏ

Vào [http://localhost:8003/carts/add-item/](http://localhost:8003/carts/add-item/), nhập vào ô **Content** rồi bấm **POST**:

```json
{
    "cart": 1,
    "book_id": 1,
    "quantity": 2
}
```

---

### Bước 5 — Xem kết quả trên giao diện

Vào [http://localhost:8000/books/](http://localhost:8000/books/) để xem **danh sách sách** trên giao diện web.

Vào [http://localhost:8000/cart/1/](http://localhost:8000/cart/1/) để xem **giỏ hàng** của customer #1.

---


## 🔧 Kiến trúc hệ thống

```
Người dùng (Browser)
        │
        ▼
  API Gateway :8000
  ┌─────┬──────┐
  │     │      │
  ▼     ▼      ▼
:8001 :8002  :8003
cust  book   cart
svc   svc    svc
```
