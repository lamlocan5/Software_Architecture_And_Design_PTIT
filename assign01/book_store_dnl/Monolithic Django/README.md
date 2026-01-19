# Monolithic Django - Book Store Application

## 📋 Tổng quan

Đây là phiên bản **Monolithic Architecture** (Kiến trúc nguyên khối) của hệ thống Book Store. Tất cả các chức năng được tích hợp trong một ứng dụng Django duy nhất với một cơ sở dữ liệu chung.

## 🏗️ Kiến trúc Monolithic

```
┌─────────────────────────────────────────────────┐
│         Monolithic Django Application           │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Books   │  │ Accounts │  │   Cart   │      │
│  │   App    │  │   App    │  │   App    │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│                                                  │
│              ┌────────────────┐                 │
│              │  Shared Models │                 │
│              │   & Database   │                 │
│              └────────────────┘                 │
└─────────────────────────────────────────────────┘
```

## 📁 Cấu trúc dự án

```
Monolithic Django/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies (if exists)
├── .env                        # Environment variables (MySQL config)
├── .gitignore                  # Git ignore patterns
├── create.sql                  # Database creation script
│
├── book_store/                 # Main Django project
│   ├── settings.py            # Project settings
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── accounts/                   # Customer authentication app
│   ├── models.py              # Customer model
│   ├── views.py               # Login, Register views
│   ├── urls.py                # Account routes
│   ├── forms.py               # Login/Register forms
│   └── admin.py               # Admin configuration
│
├── books/                      # Book catalog app
│   ├── models.py              # Book model
│   ├── views.py               # Book listing, detail views
│   ├── urls.py                # Book routes
│   └── admin.py               # Admin configuration
│
├── cart/                       # Shopping cart app
│   ├── models.py              # CartItem model
│   ├── views.py               # Cart operations
│   ├── urls.py                # Cart routes
│   └── admin.py               # Admin configuration
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── home.html              # Homepage
│   ├── books/                 # Book templates
│   ├── accounts/              # Auth templates
│   └── cart/                  # Cart templates
│
└── static/                     # Static files (CSS, JS, images)
    ├── css/
    └── js/
```

## 🎯 Tính năng

### 1. Quản lý khách hàng (Accounts App)
- ✅ Đăng ký tài khoản mới
- ✅ Đăng nhập/Đăng xuất
- ✅ Xem thông tin cá nhân
- ✅ Session management

### 2. Quản lý sách (Books App)
- ✅ Hiển thị danh sách sách
- ✅ Xem chi tiết sách
- ✅ Tìm kiếm sách (nếu có)
- ✅ Quản lý tồn kho

### 3. Giỏ hàng (Cart App)
- ✅ Thêm sách vào giỏ
- ✅ Xem giỏ hàng
- ✅ Cập nhật số lượng
- ✅ Xóa sản phẩm khỏi giỏ

## 🗃️ Database Schema

```sql
-- Customers table
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cart Items table
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);
```

## 🚀 Hướng dẫn cài đặt

### Bước 1: Cài đặt MySQL Database

1. Đảm bảo MySQL Server đang chạy
2. Tạo database bằng script:

```bash
mysql -u root -p < create.sql
```

Hoặc tạo thủ công:
```sql
CREATE DATABASE bookstore_monolithic;
```

### Bước 2: Cấu hình môi trường

Kiểm tra file `.env` với nội dung:
```env
DB_NAME=bookstore_monolithic
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

### Bước 3: Cài đặt Python dependencies

```bash
# Tạo virtual environment (khuyến nghị)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt dependencies
pip install django
pip install mysqlclient
pip install python-dotenv
```

Hoặc nếu có `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Bước 4: Migrate database

```bash
python manage.py makemigrations
python manage.py migrate
```

### Bước 5: Tạo superuser (optional)

```bash
python manage.py createsuperuser
```

### Bước 6: Chạy server

```bash
python manage.py runserver
```

Server sẽ chạy tại: **http://localhost:8000**

## 📡 URL Routes

| URL | Chức năng | Method |
|-----|-----------|--------|
| `/` | Trang chủ | GET |
| `/accounts/register/` | Đăng ký | GET, POST |
| `/accounts/login/` | Đăng nhập | GET, POST |
| `/accounts/logout/` | Đăng xuất | GET |
| `/books/` | Danh sách sách | GET |
| `/books/<id>/` | Chi tiết sách | GET |
| `/cart/` | Xem giỏ hàng | GET |
| `/cart/add/<book_id>/` | Thêm vào giỏ | POST |
| `/cart/remove/<item_id>/` | Xóa khỏi giỏ | POST |
| `/admin/` | Django Admin | GET |

## ⚙️ Django Settings

### Installed Apps
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'books',
    'cart',
]
```

### Database Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'bookstore_monolithic'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
    }
}
```

## 🧪 Testing

### Chạy tests
```bash
python manage.py test
```

### Test thủ công
1. Truy cập http://localhost:8000
2. Đăng ký tài khoản mới
3. Đăng nhập
4. Xem danh sách sách
5. Thêm sách vào giỏ
6. Kiểm tra giỏ hàng

## ✅ Ưu điểm của Monolithic

- ✅ **Đơn giản**: Dễ phát triển, dễ triển khai
- ✅ **Hiệu năng**: Không có network overhead giữa các modules
- ✅ **Debug dễ**: Tất cả code ở một chỗ
- ✅ **Transaction**: Dễ quản lý transactions giữa các tables
- ✅ **Development**: Nhanh chóng cho MVP và prototype

## ❌ Nhược điểm của Monolithic

- ❌ **Scalability**: Khó scale từng chức năng riêng lẻ
- ❌ **Maintenance**: Khó bảo trì khi project lớn
- ❌ **Deployment**: Phải deploy lại toàn bộ app khi có thay đổi nhỏ
- ❌ **Technology**: Bị ràng buộc với một technology stack
- ❌ **Team**: Khó cho nhiều team làm việc parallel

## 🐛 Troubleshooting

### Lỗi: "No module named 'mysqlclient'"
```bash
pip install mysqlclient
# Hoặc trên Windows:
pip install pymysql
```

### Lỗi: "Access denied for user 'root'@'localhost'"
- Kiểm tra file `.env`
- Đảm bảo MySQL username/password đúng

### Lỗi: "Database doesn't exist"
```bash
mysql -u root -p < create.sql
```

### Lỗi: "Port 8000 already in use"
```bash
# Chạy trên port khác
python manage.py runserver 8080
```

## 📚 Tài liệu tham khảo

- [Django Documentation](https://docs.djangoproject.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Django Models](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Views](https://docs.djangoproject.com/en/stable/topics/http/views/)

## 🔄 Migration commands

```bash
# Tạo migrations
python manage.py makemigrations

# Xem SQL sẽ được execute
python manage.py sqlmigrate accounts 0001

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate accounts 0001
```

## 👨‍💻 Development Tips

1. **Sử dụng Django Debug Toolbar** để debug queries
2. **Tạo fixtures** để test data
3. **Viết tests** cho các critical functions
4. **Sử dụng Django Admin** để quản lý data dễ dàng
5. **Enable logging** để track errors

---
**Architecture:** Monolithic  
**Framework:** Django  
**Database:** MySQL  
**Version:** 1.0
