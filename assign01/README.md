# Assignment 01 - Book Store Web System
**Software Architecture and Design - PTIT**

## 📋 Tổng quan

Đây là bài tập lớn về thiết kế kiến trúc phần mềm cho hệ thống cửa hàng sách trực tuyến (Book Store Web System). Bài tập yêu cầu thiết kế và triển khai 3 phiên bản kiến trúc khác nhau:

1. **Monolithic Architecture** - Kiến trúc nguyên khối truyền thống
2. **Clean Architecture** - Kiến trúc phân tầng rõ ràng theo Clean Architecture
3. **Microservices Architecture** - Kiến trúc vi dịch vụ phân tán

## 📁 Cấu trúc thư mục

```
assign01/
└── book_store_dnl/
    ├── 1.docx                          # Tài liệu mô tả yêu cầu chi tiết
    ├── lamdn.pdf                       # Báo cáo PDF đầy đủ
    ├── README.md                       # Hướng dẫn cài đặt và chạy hệ thống
    ├── Monolithic Django/              # Version A: Kiến trúc nguyên khối
    ├── Clean Architecture Django/      # Version B: Clean Architecture
    └── Microservices Django/           # Version C: Microservices
        ├── frontend/                   # Gateway service (Port 8000)
        ├── book-service/               # Book catalog service (Port 8002)
        ├── customer-service/           # Customer auth service (Port 8001)
        └── cart-service/               # Shopping cart service (Port 8003)
```

## 📚 Tài liệu

### 1. **1.docx** - Tài liệu yêu cầu chi tiết
Mô tả các yêu cầu chức năng và phi chức năng của hệ thống, bao gồm:
- Yêu cầu về quản lý sách
- Yêu cầu về xác thực khách hàng
- Yêu cầu về giỏ hàng
- Thiết kế cơ sở dữ liệu MySQL

### 2. **lamdn.pdf** - Báo cáo tổng hợp
Báo cáo PDF hoàn chỉnh bao gồm:
- UML Class Diagram
- MVC Architecture Diagram
- Clean Architecture Diagram
- Microservices Architecture Diagram
- Mô tả chi tiết từng phiên bản
- So sánh ưu/nhược điểm các kiến trúc

### 3. **README.md** - Hướng dẫn triển khai
Hướng dẫn cài đặt và chạy từng phiên bản của hệ thống

## 🎯 Yêu cầu chức năng

### 1. **Quản lý sách (Book Management)**
- Hiển thị danh sách sách
- Xem chi tiết thông tin sách
- Quản lý kho hàng (stock)

### 2. **Xác thực khách hàng (Customer Authentication)**
- Đăng ký tài khoản mới
- Đăng nhập
- Quản lý thông tin cá nhân

### 3. **Giỏ hàng (Shopping Cart)**
- Thêm sách vào giỏ
- Xem giỏ hàng
- Xóa sách khỏi giỏ
- Cập nhật số lượng

## 🏗️ Kiến trúc hệ thống

### Version A: Monolithic Architecture
```
┌─────────────────────────────────┐
│      Monolithic Django App      │
│  ┌───────┬──────────┬────────┐  │
│  │ Books │ Customer │  Cart  │  │
│  └───────┴──────────┴────────┘  │
│         Single Database          │
└─────────────────────────────────┘
```

**Đặc điểm:**
- Tất cả chức năng trong 1 project Django
- Dễ triển khai và phát triển ban đầu
- Khó mở rộng khi hệ thống lớn

### Version B: Clean Architecture
```
┌─────────────────────────────────────┐
│  Presentation Layer (Views/API)     │
├─────────────────────────────────────┤
│  Application Layer (Use Cases)      │
├─────────────────────────────────────┤
│  Domain Layer (Entities/Business)   │
├─────────────────────────────────────┤
│  Infrastructure Layer (DB/External) │
└─────────────────────────────────────┘
```

**Đặc điểm:**
- Phân tầng rõ ràng, dễ bảo trì
- Business logic độc lập với framework
- Dễ test và mở rộng

### Version C: Microservices Architecture
```
                    ┌─────────────────┐
                    │  Frontend (8000) │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐
    │ Customer  │     │   Book    │     │   Cart    │
    │ Service   │     │  Service  │     │  Service  │
    │  (8001)   │     │  (8002)   │     │  (8003)   │
    └───────────┘     └───────────┘     └───────────┘
         │                 │                 │
    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
    │   DB    │       │   DB    │       │   DB    │
    └─────────┘       └─────────┘       └─────────┘
```

**Đặc điểm:**
- Mỗi service độc lập, có database riêng
- Dễ scale từng service
- Phức tạp trong triển khai và quản lý

## 🚀 Hướng dẫn chạy nhanh

### Yêu cầu hệ thống
- Python 3.10+
- MySQL Server (localhost:3306)
- pip (Python package manager)

### Chạy Monolithic Version
```bash
cd "assign01/book_store_dnl/Monolithic Django"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Truy cập: http://localhost:8000

### Chạy Clean Architecture Version
```bash
cd "assign01/book_store_dnl/Clean Architecture Django"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Truy cập: http://localhost:8000

### Chạy Microservices Version
Cần chạy 4 services đồng thời trong 4 terminal khác nhau:

**Terminal 1 - Customer Service:**
```bash
cd "assign01/book_store_dnl/Microservices Django/customer-service"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

**Terminal 2 - Book Service:**
```bash
cd "assign01/book_store_dnl/Microservices Django/book-service"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

**Terminal 3 - Cart Service:**
```bash
cd "assign01/book_store_dnl/Microservices Django/cart-service"
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8003
```

**Terminal 4 - Frontend Gateway:**
```bash
cd "assign01/book_store_dnl/Microservices Django/frontend"
pip install -r requirements.txt
python manage.py runserver 8000
```

Truy cập: http://localhost:8000

## 🔗 API Endpoints (Microservices)

### Customer Service (Port 8001)
- `POST /api/register/` - Đăng ký tài khoản
- `POST /api/login/` - Đăng nhập
- `GET /api/customers/<id>/` - Xem thông tin khách hàng

### Book Service (Port 8002)
- `GET /api/books/` - Danh sách sách
- `GET /api/books/<id>/` - Chi tiết sách
- `PATCH /api/books/<id>/stock/` - Cập nhật kho

### Cart Service (Port 8003)
- `POST /api/cart/add/` - Thêm vào giỏ
- `GET /api/cart/<customer_id>/` - Xem giỏ hàng
- `DELETE /api/cart/items/<id>/` - Xóa khỏi giỏ

## 🗃️ Database Schema

Hệ thống sử dụng MySQL với các bảng chính:

- **books** - Thông tin sách
- **customers** - Thông tin khách hàng
- **cart_items** - Sản phẩm trong giỏ hàng

Chi tiết schema xem trong file `lamdn.pdf`

## 📊 So sánh các kiến trúc

| Tiêu chí | Monolithic | Clean Architecture | Microservices |
|----------|------------|-------------------|---------------|
| **Độ phức tạp** | Thấp | Trung bình | Cao |
| **Khả năng mở rộng** | Khó | Trung bình | Dễ |
| **Thời gian phát triển** | Nhanh | Trung bình | Chậm |
| **Bảo trì** | Khó (khi lớn) | Dễ | Dễ |
| **Testing** | Khó tách biệt | Dễ test | Dễ test độc lập |
| **Deployment** | Đơn giản | Đơn giản | Phức tạp |
| **Độc lập công nghệ** | Không | Có | Có |

## 👨‍💻 Tác giả

- **Sinh viên:** [Tên sinh viên]
- **Lớp:** [Mã lớp]
- **Môn học:** Software Architecture and Design
- **Trường:** PTIT (Học viện Công nghệ Bưu chính Viễn thông)

## 📝 Ghi chú

- Tất cả 3 phiên bản đều sử dụng Django framework
- Database: MySQL
- Hướng dẫn chi tiết và troubleshooting xem trong `README.md` của từng version
- UML diagrams và phân tích chi tiết xem trong `lamdn.pdf`

## 📧 Liên hệ

Nếu có thắc mắc về bài tập, vui lòng liên hệ qua email hoặc GitHub issues.

---
**Last Updated:** January 2026
