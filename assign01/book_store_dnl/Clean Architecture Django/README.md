# Clean Architecture Django - Book Store Application

## 📋 Tổng quan

Đây là phiên bản **Clean Architecture** của hệ thống Book Store. Kiến trúc này phân tách rõ ràng các tầng (layers) để tăng tính module hóa, dễ test và bảo trì. Business logic hoàn toàn độc lập với framework và infrastructure.

## 🏗️ Clean Architecture Principles

```
┌─────────────────────────────────────────────────────────┐
│                    Interfaces Layer                     │
│              (Controllers, Views, APIs)                 │
├─────────────────────────────────────────────────────────┤
│                     Use Cases Layer                     │
│         (Application Business Rules/Logic)              │
├─────────────────────────────────────────────────────────┤
│                      Domain Layer                       │
│          (Enterprise Business Rules/Entities)           │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                   │
│        (Database, External APIs, Framework)             │
└─────────────────────────────────────────────────────────┘

 Dependency Rule: Inner layers không phụ thuộc vào outer layers
```

## 📁 Cấu trúc dự án

```
Clean Architecture Django/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore patterns
├── create.sql                  # Database creation script
│
├── framework/                  # Framework configuration
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration
│
├── domain/                     # 🔵 DOMAIN LAYER (Core Business)
│   ├── __init__.py
│   ├── entities/              # Business entities
│   │   ├── customer.py        # Customer entity
│   │   ├── book.py            # Book entity
│   │   └── cart_item.py       # CartItem entity
│   └── repositories/          # Repository interfaces
│       ├── customer_repo.py
│       ├── book_repo.py
│       └── cart_repo.py
│
├── usecases/                   # 🟢 USE CASES LAYER (Application Logic)
│   ├── __init__.py
│   ├── customer/
│   │   ├── register_customer.py    # Register use case
│   │   ├── login_customer.py       # Login use case
│   │   └── get_customer.py         # Get customer info
│   ├── book/
│   │   ├── list_books.py           # List all books
│   │   ├── get_book_detail.py      # Get book details
│   │   └── update_stock.py         # Update book stock
│   └── cart/
│       ├── add_to_cart.py          # Add item to cart
│       ├── view_cart.py            # View cart
│       └── remove_from_cart.py     # Remove from cart
│
├── infrastructure/             # 🟡 INFRASTRUCTURE LAYER (External)
│   ├── __init__.py
│   ├── database/
│   │   ├── models.py          # Django ORM models
│   │   └── migrations/        # Database migrations
│   └── repositories/          # Repository implementations
│       ├── django_customer_repo.py
│       ├── django_book_repo.py
│       └── django_cart_repo.py
│
├── interfaces/                 # 🔴 INTERFACES LAYER (Presentation)
│   ├── __init__.py
│   ├── web/                   # Web interface
│   │   ├── views.py           # Django views/controllers
│   │   ├── urls.py            # URL routing
│   │   └── forms.py           # Django forms
│   └── api/                   # REST API (if exists)
│       └── serializers.py
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── books/
│   │   ├── list.html
│   │   └── detail.html
│   ├── accounts/
│   │   ├── login.html
│   │   └── register.html
│   └── cart/
│       └── view.html
│
└── static/                     # Static files
    └── css/
        └── styles.css
```

## 🎯 Clean Architecture Layers

### 1. 🔵 Domain Layer (Innermost)
**Mục đích:** Chứa business logic thuần túy, entities và repository interfaces

**Đặc điểm:**
- ✅ Không phụ thuộc vào framework
- ✅ Không phụ thuộc vào database
- ✅ Chỉ chứa Python code thuần
- ✅ Dễ test nhất

**Ví dụ:**
```python
# domain/entities/book.py
class Book:
    def __init__(self, id, title, author, price, stock):
        self.id = id
        self.title = title
        self.author = author
        self.price = price
        self.stock = stock
    
    def is_available(self):
        return self.stock > 0
```

### 2. 🟢 Use Cases Layer
**Mục đích:** Chứa application business logic, orchestrate các entities

**Đặc điểm:**
- ✅ Chỉ phụ thuộc vào Domain layer
- ✅ Điều phối các entities và repositories
- ✅ Chứa business rules của application
- ✅ Framework-agnostic

**Ví dụ:**
```python
# usecases/book/list_books.py
class ListBooksUseCase:
    def __init__(self, book_repository):
        self.book_repository = book_repository
    
    def execute(self):
        return self.book_repository.get_all()
```

### 3. 🟡 Infrastructure Layer
**Mục đích:** Implement các repository interfaces, database access

**Đặc điểm:**
- ✅ Implement domain repository interfaces
- ✅ Django ORM models ở đây
- ✅ Database migrations
- ✅ External API integrations

**Ví dụ:**
```python
# infrastructure/repositories/django_book_repo.py
class DjangoBookRepository(BookRepository):
    def get_all(self):
        books = BookModel.objects.all()
        return [self._to_entity(book) for book in books]
```

### 4. 🔴 Interfaces Layer (Outermost)
**Mục đích:** Handle HTTP requests, present data to users

**Đặc điểm:**
- ✅ Django views/controllers
- ✅ Forms và serializers
- ✅ URL routing
- ✅ Input validation

**Ví dụ:**
```python
# interfaces/web/views.py
def book_list_view(request):
    use_case = ListBooksUseCase(book_repository)
    books = use_case.execute()
    return render(request, 'books/list.html', {'books': books})
```

## 🗃️ Database Schema

Database schema tương tự Monolithic version (xem `create.sql`):

```sql
-- Customers, Books, Cart Items tables
-- Chi tiết xem trong create.sql
```

## 🚀 Hướng dẫn cài đặt

### Bước 1: Setup MySQL Database

```bash
mysql -u root -p < create.sql
```

Hoặc:
```sql
CREATE DATABASE bookstore_clean;
```

### Bước 2: Cấu hình Environment

File `.env`:
```env
DB_NAME=bookstore_clean
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=your-secret-key
DEBUG=True
```

### Bước 3: Cài đặt Dependencies

```bash
# Tạo virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Cài đặt packages
pip install -r requirements.txt
```

**requirements.txt:**
```txt
Django>=4.0
mysqlclient
python-dotenv
```

### Bước 4: Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### Bước 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Bước 6: Run Development Server

```bash
python manage.py runserver
```

Truy cập: **http://localhost:8000**

## 📡 Application Flow

### Ví dụ: User đăng ký tài khoản

```
1. [User] → Submit form
         ↓
2. [Interface] views.py → Validate input
         ↓
3. [Use Case] register_customer.py → Business logic
         ↓
4. [Domain] Customer entity → Create customer
         ↓
5. [Infrastructure] DjangoCustomerRepo → Save to DB
         ↓
6. [Interface] → Render success page
```

### Ví dụ: Thêm sách vào giỏ

```
1. [User] → Click "Add to Cart"
         ↓
2. [Interface] views.py → Get book_id, customer_id
         ↓
3. [Use Case] add_to_cart.py → Check stock, create cart item
         ↓
4. [Domain] CartItem entity → Validate quantity
         ↓
5. [Infrastructure] DjangoCartRepo → Save to DB
         ↓
6. [Infrastructure] DjangoBookRepo → Update stock
         ↓
7. [Interface] → Redirect to cart page
```

## ✅ Ưu điểm Clean Architecture

- ✅ **Testability**: Dễ test từng layer độc lập
- ✅ **Maintainability**: Dễ bảo trì, sửa lỗi
- ✅ **Framework Independence**: Có thể đổi Django sang Flask
- ✅ **Database Independence**: Có thể đổi MySQL sang PostgreSQL
- ✅ **Business Logic Protection**: Core logic không bị ảnh hưởng bởi UI/DB
- ✅ **Team Collaboration**: Nhiều team làm việc song song dễ dàng
- ✅ **Scalability**: Dễ mở rộng chức năng mới

## ❌ Nhược điểm Clean Architecture

- ❌ **Complexity**: Phức tạp hơn monolithic
- ❌ **Learning Curve**: Cần hiểu rõ các layers
- ❌ **Boilerplate**: Nhiều code boilerplate
- ❌ **Initial Development**: Chậm hơn ở giai đoạn đầu
- ❌ **Over-engineering**: Có thể quá mức cần thiết cho project nhỏ

## 🧪 Testing Strategy

### Unit Testing

**Domain Layer:**
```python
# test_book_entity.py
def test_book_is_available():
    book = Book(1, "Title", "Author", 10.0, 5)
    assert book.is_available() == True
```

**Use Cases Layer:**
```python
# test_list_books_usecase.py
def test_list_books():
    mock_repo = Mock(BookRepository)
    use_case = ListBooksUseCase(mock_repo)
    books = use_case.execute()
    assert len(books) > 0
```

**Infrastructure Layer:**
```python
# test_django_book_repo.py
def test_get_all_books():
    repo = DjangoBookRepository()
    books = repo.get_all()
    assert isinstance(books, list)
```

### Integration Testing

```bash
python manage.py test
```

## 🔧 Dependency Injection

Clean Architecture sử dụng Dependency Injection:

```python
# Tạo repository instances
customer_repo = DjangoCustomerRepository()
book_repo = DjangoBookRepository()
cart_repo = DjangoCartRepository()

# Inject vào use cases
register_use_case = RegisterCustomerUseCase(customer_repo)
list_books_use_case = ListBooksUseCase(book_repo)
add_to_cart_use_case = AddToCartUseCase(cart_repo, book_repo)

# Sử dụng trong views
def register_view(request):
    result = register_use_case.execute(data)
    return render(request, 'success.html')
```

## 📚 Design Patterns Used

1. **Repository Pattern**: Abstracts data access
2. **Use Case Pattern**: Encapsulates business logic
3. **Dependency Injection**: Loose coupling
4. **Entity Pattern**: Domain models
5. **Adapter Pattern**: Framework adapters

## 🐛 Troubleshooting

### Import errors
```python
# Đảm bảo __init__.py trong mỗi folder
# Sử dụng absolute imports
from domain.entities.book import Book
```

### Circular dependencies
```
# Tránh import lẫn nhau giữa các layers
# Domain không được import Infrastructure
```

### Database connection issues
```bash
# Kiểm tra .env file
# Test MySQL connection
mysql -u root -p
```

## 🔄 So sánh với Monolithic

| Tiêu chí | Monolithic | Clean Architecture |
|----------|------------|-------------------|
| **Complexity** | Thấp | Trung bình - Cao |
| **Testability** | Khó | Rất dễ |
| **Maintainability** | Khó (khi lớn) | Rất tốt |
| **Framework Lock-in** | Có | Không |
| **Initial Speed** | Nhanh | Chậm hơn |
| **Long-term** | Khó scale | Dễ scale |

## 📖 Tài liệu tham khảo

- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Django Best Practices](https://docs.djangoproject.com/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)

---
**Architecture:** Clean Architecture  
**Framework:** Django  
**Database:** MySQL  
**Layers:** 4 (Domain, Use Cases, Infrastructure, Interfaces)  
**Version:** 2.0
