# 📚 Django Bookstore Application

Hệ thống quản lý cửa hàng sách trực tuyến được xây dựng với Django và MySQL, theo kiến trúc MVC.

## 🎯 Tính năng chính

### Khách hàng
- ✅ Đăng ký và đăng nhập tài khoản
- ✅ Quản lý thông tin cá nhân và địa chỉ
- ✅ Duyệt và tìm kiếm sách
- ✅ Lọc theo danh mục, tác giả
- ✅ Xem chi tiết sách và đánh giá
- ✅ Thêm vào giỏ hàng và wishlist
- ✅ Đặt hàng và thanh toán
- ✅ Xem lịch sử đơn hàng

### Nhân viên
- ✅ Dashboard thống kê
- ✅ Quản lý đơn hàng
- ✅ Quản lý tồn kho
- ✅ Quản lý khách hàng
- ✅ Báo cáo doanh thu

## 📋 Yêu cầu hệ thống

- Python 3.8 trở lên
- MySQL 5.7 trở lên
- pip (Python package manager)

## 🚀 Hướng dẫn cài đặt

### 1. Clone hoặc tải project

```bash
cd bookstore02_prj
```

### 2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình MySQL Database

#### Tạo database trong MySQL:

```sql
CREATE DATABASE bookstore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Cập nhật thông tin database trong `bookstore/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bookstore_db',
        'USER': 'root',  # Thay bằng MySQL username của bạn
        'PASSWORD': '',  # Thay bằng MySQL password của bạn
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Chạy migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Tạo superuser (admin)

```bash
python manage.py createsuperuser
```

Nhập thông tin:
- Username
- Email
- Password

### 7. Chạy development server

```bash
python manage.py runserver
```

Mở trình duyệt và truy cập: `http://localhost:8000`

## 📁 Cấu trúc thư mục

```
bookstore02_prj/
│
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── README.md                      # Tài liệu hướng dẫn
│
├── bookstore/                     # Django project settings
│   ├── __init__.py
│   ├── settings.py               # Cấu hình project
│   ├── urls.py                   # Main URL routing
│   └── wsgi.py                   # WSGI configuration
│
└── store/                        # Main application
    ├── __init__.py
    ├── apps.py                   # App configuration
    ├── admin.py                  # Django admin configuration
    │
    ├── models/                   # Data models
    │   ├── __init__.py
    │   ├── customer.py           # Customer, Address
    │   ├── book.py               # Book, Author, Publisher, Category, Review
    │   ├── order.py              # Order, OrderItem, Cart, Wishlist, Shipping
    │   └── staff.py              # Staff
    │
    ├── controllers/              # Views/Controllers (MVC pattern)
    │   ├── __init__.py
    │   ├── customerController.py # Customer operations
    │   ├── bookController.py     # Book catalog operations
    │   ├── orderController.py    # Cart, checkout, orders
    │   └── staffController.py    # Staff dashboard
    │
    ├── urls/                     # URL routing modules
    │   ├── customer_urls.py
    │   ├── book_urls.py
    │   ├── order_urls.py
    │   └── staff_urls.py
    │
    └── templates/                # HTML templates
        ├── base.html             # Base template
        ├── book/
        │   ├── list.html         # Book listing
        │   └── detail.html       # Book details
        ├── cart/
        │   ├── view.html         # Shopping cart
        │   └── checkout.html     # Checkout page
        └── staff/
            └── dashboard.html    # Staff dashboard
```

## 🗄️ Database Schema

Project sử dụng các bảng sau (dựa trên ER diagram):

- **Customer**: Thông tin khách hàng
- **Address**: Địa chỉ giao hàng
- **Book**: Thông tin sách
- **Author**: Tác giả
- **Publisher**: Nhà xuất bản
- **Category**: Danh mục sách
- **BookAuthor**: Liên kết Book-Author (many-to-many)
- **BookCategory**: Liên kết Book-Category (many-to-many)
- **Review**: Đánh giá của khách hàng
- **Order**: Đơn hàng
- **OrderItem**: Chi tiết đơn hàng
- **Cart**: Giỏ hàng
- **Wishlist**: Danh sách yêu thích
- **Shipping**: Thông tin vận chuyển
- **Staff**: Nhân viên

## 🔑 Truy cập hệ thống

### Admin Panel
- URL: `http://localhost:8000/admin/`
- Đăng nhập bằng superuser đã tạo ở bước 6

### Customer Interface
- Trang chủ: `http://localhost:8000/`
- Đăng ký: `http://localhost:8000/customer/register/`
- Đăng nhập: `http://localhost:8000/customer/login/`

### Staff Dashboard
- URL: `http://localhost:8000/staff/login/`
- Tạo staff account qua admin panel trước

## 📌 API Endpoints

### Customer
- `GET /customer/register/` - Đăng ký
- `POST /customer/login/` - Đăng nhập
- `GET /customer/profile/` - Xem/Sửa profile
- `POST /customer/address/add/` - Thêm địa chỉ

### Books
- `GET /` - Danh sách sách
- `GET /book/<id>/` - Chi tiết sách
- `GET /search/` - Tìm kiếm
- `POST /book/<id>/review/` - Thêm đánh giá

### Cart & Orders
- `GET /cart/` - Xem giỏ hàng
- `POST /cart/add/<book_id>/` - Thêm vào giỏ
- `POST /cart/checkout/` - Thanh toán
- `GET /cart/orders/` - Lịch sử đơn hàng

### Staff
- `POST /staff/login/` - Đăng nhập staff
- `GET /staff/dashboard/` - Dashboard
- `GET /staff/orders/` - Quản lý đơn hàng
- `GET /staff/inventory/` - Quản lý kho

## 🛠️ Thêm dữ liệu mẫu

1. Truy cập Admin Panel: `http://localhost:8000/admin/`
2. Thêm dữ liệu cho các bảng:
   - Author (Tác giả)
   - Publisher (Nhà xuất bản)
   - Category (Danh mục)
   - Book (Sách)
   - Staff (Nhân viên)

Hoặc sử dụng Django shell:

```bash
python manage.py shell
```

```python
from store.models import *

# Tạo tác giả
author = Author.objects.create(name="Nguyễn Nhật Ánh", biography="Nhà văn Việt Nam nổi tiếng")

# Tạo nhà xuất bản
publisher = Publisher.objects.create(name="NXB Trẻ", email="nxbtre@example.com")

# Tạo danh mục
category = Category.objects.create(name="Văn học", description="Sách văn học")

# Tạo sách
book = Book.objects.create(
    title="Tôi Thấy Hoa Vàng Trên Cỏ Xanh",
    isbn="978-604-1-00000-0",
    description="Tác phẩm văn học hay",
    price=85000,
    stock=100,
    publisher=publisher
)
book.authors.add(author)
book.categories.add(category)
```

## 🔧 Troubleshooting

### Lỗi kết nối MySQL
```
django.db.utils.OperationalError: (2002, "Can't connect to MySQL server")
```
**Giải pháp**: Kiểm tra MySQL đã chạy chưa và thông tin kết nối trong `settings.py`

### Lỗi mysqlclient
```
OSError: mysql_config not found
```
**Giải pháp**: 
- Windows: Cài MySQL Connector/C
- Linux: `sudo apt-get install python3-dev default-libmysqlclient-dev build-essential`
- Mac: `brew install mysql`

### Lỗi migrations
```
python manage.py migrate --run-syncdb
```

## 📝 Ghi chú

- Môi trường development sử dụng `DEBUG = True` trong `settings.py`
- Khi deploy production, nhớ:
  - Đặt `DEBUG = False`
  - Thay đổi `SECRET_KEY`
  - Cập nhật `ALLOWED_HOSTS`
  - Cấu hình static files và media files
  - Sử dụng HTTPS

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng tạo issue hoặc liên hệ team phát triển.

---

**Developed with ❤️ using Django & MySQL**
