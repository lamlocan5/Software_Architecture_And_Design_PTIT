# Book Service

## 📋 Tổng quan

Book Service là microservice chịu trách nhiệm quản lý catalog sách và tồn kho (inventory). Service này hoạt động độc lập với database riêng và expose REST APIs để các services khác có thể truy cập thông tin sách.

## 🎯 Trách nhiệm

- 📚 Quản lý catalog sách (CRUD operations)
- 📦 Quản lý tồn kho (stock management)
- 🔍 Tìm kiếm và lọc sách
- 💰 Quản lý giá sách
- 📊 Provide book data cho các services khác

## 🏗️ Kiến trúc

```
┌─────────────────────────────────┐
│     Book Service (:8002)        │
│                                 │
│  ┌─────────────────────────┐   │
│  │    REST API Layer       │   │
│  │  (views, serializers)   │   │
│  └───────────┬─────────────┘   │
│              │                  │
│  ┌───────────▼─────────────┐   │
│  │   Business Logic Layer  │   │
│  │  (Stock validation)     │   │
│  └───────────┬─────────────┘   │
│              │                  │
│  ┌───────────▼─────────────┐   │
│  │    Django ORM Models    │   │
│  └───────────┬─────────────┘   │
└──────────────┼──────────────────┘
               │
      ┌────────▼────────┐
      │    book_db      │
      │    (MySQL)      │
      └─────────────────┘
```

## 📁 Cấu trúc

```
book-service/
├── manage.py                      # Django management
├── requirements.txt               # Dependencies
│
├── book_service/                 # Django project
│   ├── __init__.py
│   ├── settings.py              # Database: book_db
│   ├── urls.py                  # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
│
└── books/                        # Django app
    ├── __init__.py
    ├── models.py                # Book model
    ├── views.py                 # API views
    ├── serializers.py           # DRF serializers
    ├── urls.py                  # App URL routes
    ├── admin.py                 # Admin config
    └── migrations/              # Database migrations
        └── ...
```

## 🗃️ Database Schema

**Database:** `book_db`

**Table:** `books`

```sql
CREATE TABLE books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    isbn VARCHAR(13) UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    description TEXT,
    publisher VARCHAR(255),
    published_date DATE,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_category (category),
    CONSTRAINT chk_price CHECK (price >= 0),
    CONSTRAINT chk_stock CHECK (stock >= 0)
);
```

## 💻 Models

```python
# books/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    published_date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def is_available(self):
        """Check if book is in stock"""
        return self.stock > 0
    
    def decrease_stock(self, quantity=1):
        """Decrease stock (used when adding to cart)"""
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False
    
    def increase_stock(self, quantity=1):
        """Increase stock (restock or return)"""
        self.stock += quantity
        self.save()
```

## 📡 API Endpoints

### 1. List All Books
**GET** `/api/books/`

**Query Parameters:**
- `category` (optional) - Filter by category
- `search` (optional) - Search in title/author

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "price": "29.99",
    "stock": 15,
    "description": "A handbook of agile software craftsmanship",
    "publisher": "Prentice Hall",
    "published_date": "2008-08-01",
    "category": "Programming",
    "created_at": "2026-01-20T00:00:00Z"
  },
  ...
]
```

---

### 2. Get Book Details
**GET** `/api/books/<id>/`

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "9780132350884",
  "price": "29.99",
  "stock": 15,
  "description": "A handbook of agile software craftsmanship",
  "publisher": "Prentice Hall",
  "published_date": "2008-08-01",
  "category": "Programming",
  "is_available": true
}
```

**Errors:**
- `404 Not Found` - Book doesn't exist

---

### 3. Create Book (Admin)
**POST** `/api/books/`

**Request:**
```json
{
  "title": "Design Patterns",
  "author": "Gang of Four",
  "isbn": "9780201633610",
  "price": "39.99",
  "stock": 20,
  "description": "Elements of Reusable Object-Oriented Software",
  "publisher": "Addison-Wesley",
  "category": "Programming"
}
```

**Response:** `201 Created`

---

### 4. Update Book
**PUT/PATCH** `/api/books/<id>/`

**Request:**
```json
{
  "price": "34.99",
  "stock": 25
}
```

**Response:** `200 OK`

---

### 5. Delete Book
**DELETE** `/api/books/<id>/`

**Response:** `204 No Content`

---

### 6. Update Stock
**PATCH** `/api/books/<id>/stock/`

**Request:**
```json
{
  "stock": 30
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Clean Code",
  "stock": 30,
  "message": "Stock updated successfully"
}
```

---

### 7. Decrease Stock (Internal API)
**POST** `/api/books/<id>/decrease-stock/`

**Request:**
```json
{
  "quantity": 2
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "remaining_stock": 13
}
```

**Errors:**
- `400 Bad Request` - Insufficient stock

---

### 8. Check Availability
**GET** `/api/books/<id>/availability/`

**Response:** `200 OK`
```json
{
  "book_id": 1,
  "title": "Clean Code",
  "available": true,
  "stock": 15
}
```

## 💻 Code Implementation

### Serializers

```python
# books/serializers.py
from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """Full book serializer"""
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view"""
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'stock', 'is_available']


class StockUpdateSerializer(serializers.Serializer):
    """Stock update serializer"""
    stock = serializers.IntegerField(min_value=0)


class StockDecreaseSerializer(serializers.Serializer):
    """Stock decrease serializer"""
    quantity = serializers.IntegerField(min_value=1)
```

### Views

```python
# books/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Book
from .serializers import (
    BookSerializer, 
    BookListSerializer,
    StockUpdateSerializer,
    StockDecreaseSerializer
)

class BookViewSet(viewsets.ModelViewSet):
    """CRUD operations for books"""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_serializer_class(self):
        """Use lightweight serializer for list"""
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer
    
    def get_queryset(self):
        """Filter queryset based on query params"""
        queryset = Book.objects.all()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        # Search in title and author
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(author__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def stock(self, request, pk=None):
        """Update book stock"""
        book = self.get_object()
        serializer = StockUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            book.stock = serializer.validated_data['stock']
            book.save()
            return Response({
                'id': book.id,
                'title': book.title,
                'stock': book.stock,
                'message': 'Stock updated successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def decrease_stock(self, request, pk=None):
        """Decrease book stock (for cart service)"""
        book = self.get_object()
        serializer = StockDecreaseSerializer(data=request.data)
        
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            if book.decrease_stock(quantity):
                return Response({
                    'success': True,
                    'remaining_stock': book.stock
                })
            else:
                return Response(
                    {'error': 'Insufficient stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Check book availability"""
        book = self.get_object()
        return Response({
            'book_id': book.id,
            'title': book.title,
            'available': book.is_available(),
            'stock': book.stock
        })
```

### URLs

```python
# books/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

```python
# book_service/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('books.urls')),
]
```

## ⚙️ Settings

```python
# book_service/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('BOOK_DB_NAME', 'book_db'),
        'USER': os.getenv('BOOK_DB_USER', 'root'),
        'PASSWORD': os.getenv('BOOK_DB_PASSWORD', ''),
        'HOST': os.getenv('BOOK_DB_HOST', 'localhost'),
        'PORT': os.getenv('BOOK_DB_PORT', '3306'),
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'books',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}
```

## 🚀 Installation & Setup

### Step 1: Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE book_db;
```

### Step 2: Install Dependencies

```bash
cd book-service

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

**requirements.txt:**
```txt
Django>=4.0
djangorestframework>=3.14
mysqlclient
python-dotenv
```

### Step 3: Configure Environment

`.env` file:
```env
BOOK_DB_NAME=book_db
BOOK_DB_USER=root
BOOK_DB_PASSWORD=
BOOK_DB_HOST=localhost
BOOK_DB_PORT=3306
SECRET_KEY=your-secret-key
DEBUG=True
```

### Step 4: Migrate & Run

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 8002
```

Service at: **http://localhost:8002**

## 🧪 Testing APIs

### Using cURL

```bash
# List all books
curl http://localhost:8002/api/books/

# Get book details
curl http://localhost:8002/api/books/1/

# Create book
curl -X POST http://localhost:8002/api/books/ \
  -H "Content-Type: application/json" \
  -d '{"title":"Clean Code","author":"Robert Martin","price":"29.99","stock":10}'

# Update stock
curl -X PATCH http://localhost:8002/api/books/1/stock/ \
  -H "Content-Type: application/json" \
  -d '{"stock":20}'

# Check availability
curl http://localhost:8002/api/books/1/availability/

# Search books
curl "http://localhost:8002/api/books/?search=clean"

# Filter by category
curl "http://localhost:8002/api/books/?category=Programming"
```

### Using Python

```python
import requests

# List books
response = requests.get('http://localhost:8002/api/books/')
books = response.json()

# Get book
response = requests.get('http://localhost:8002/api/books/1/')
book = response.json()

# Create book
response = requests.post('http://localhost:8002/api/books/', json={
    'title': 'Design Patterns',
    'author': 'Gang of Four',
    'price': '39.99',
    'stock': 15
})

# Decrease stock
response = requests.post('http://localhost:8002/api/books/1/decrease-stock/', 
                        json={'quantity': 2})
print(response.json())
```

## 📊 Admin Panel

```python
# books/admin.py
from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'price', 'stock', 'is_available']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
```

Access admin at: http://localhost:8002/admin/

## 🔐 Business Rules

1. **Stock Validation**: Stock cannot be negative
2. **Price Validation**: Price must be > 0
3. **ISBN Uniqueness**: ISBN must be unique if provided
4. **Availability**: Book is available if stock > 0
5. **Atomic Stock Updates**: Use database transactions

## 🐛 Troubleshooting

```bash
# Check service is running
curl http://localhost:8002/api/books/

# Database connection
mysql -u root -p book_db -e "SELECT COUNT(*) FROM books;"

# Reset migrations
python manage.py migrate books zero
python manage.py migrate
```

## 📈 Performance Optimization

```python
# Add database indexes
class Book(models.Model):
    # ...
    class Meta:
        indexes = [
            models.Index(fields=['title', 'author']),
            models.Index(fields=['category', 'price']),
        ]

# Use select_related for FKs (if added later)
books = Book.objects.select_related('publisher')

# Add caching
from django.core.cache import cache

def get_book(book_id):
    cache_key = f'book_{book_id}'
    book = cache.get(cache_key)
    if not book:
        book = Book.objects.get(id=book_id)
        cache.set(cache_key, book, 300)  # 5 minutes
    return book
```

---
**Port:** 8002  
**Database:** book_db (MySQL)  
**Framework:** Django REST Framework  
**Domain:** Book Catalog & Inventory
