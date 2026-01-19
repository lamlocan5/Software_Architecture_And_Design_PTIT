# Cart Service

## 📋 Tổng quan

Cart Service là microservice chịu trách nhiệm quản lý giỏ hàng của khách hàng. Service này lưu trữ các items trong giỏ hàng với database riêng và tương tác với Book Service & Customer Service qua REST APIs.

## 🎯 Trách nhiệm

- 🛒 Quản lý giỏ hàng của khách hàng
- ➕ Thêm/xóa items khỏi giỏ
- 🔢 Cập nhật số lượng items
- 💰 Tính tổng giá trị giỏ hàng
- 🔗 Tương tác với Book Service để lấy thông tin sách
- 🔗 Tương tác với Customer Service để verify customer

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────────┐
│      Cart Service (:8003)               │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │      REST API Layer             │   │
│  │   (views, serializers)          │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │    Business Logic Layer         │   │
│  │  (Cart calculations, HTTP       │   │
│  │   clients to other services)    │   │
│  └──────────────┬──────────────────┘   │
│                 │                       │
│  ┌──────────────▼──────────────────┐   │
│  │      Django ORM Models          │   │
│  └──────────────┬──────────────────┘   │
└─────────────────┼────────────────────────┘
                  │
         ┌────────▼────────┐
         │    cart_db      │
         │    (MySQL)      │
         └─────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌────▼────┐
    │Customer │      │  Book   │
    │Service  │      │ Service │
    │ :8001   │      │  :8002  │
    └─────────┘      └─────────┘
```

## 📁 Cấu trúc

```
cart-service/
├── manage.py                      # Django management
├── requirements.txt               # Dependencies
│
├── cart_service/                 # Django project
│   ├── __init__.py
│   ├── settings.py              # Database: cart_db
│   ├── urls.py                  # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
│
└── carts/                        # Django app
    ├── __init__.py
    ├── models.py                # CartItem model
    ├── views.py                 # API views
    ├── serializers.py           # DRF serializers
    ├── urls.py                  # App URL routes
    ├── services.py              # HTTP clients for external APIs
    ├── admin.py                 # Admin config
    └── migrations/              # Database migrations
        └── ...
```

## 🗃️ Database Schema

**Database:** `cart_db`

**Table:** `cart_items`

```sql
CREATE TABLE cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_book_id (book_id),
    UNIQUE KEY unique_customer_book (customer_id, book_id),
    CONSTRAINT chk_quantity CHECK (quantity > 0)
);
```

**Note:** 
- `customer_id` và `book_id` là foreign key references đến các services khác
- **KHÔNG có database-level foreign key constraints** (microservices pattern)
- Data integrity được maintain qua API calls

## 💻 Models

```python
# carts/models.py
from django.db import models
from django.core.validators import MinValueValidator

class CartItem(models.Model):
    # Reference IDs to other services (no FK constraints!)
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['customer_id', 'book_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_id']),
            models.Index(fields=['book_id']),
        ]
    
    def __str__(self):
        return f"CartItem(customer={self.customer_id}, book={self.book_id}, qty={self.quantity})"
```

## 📡 API Endpoints

### 1. Get Customer's Cart
**GET** `/api/cart/<customer_id>/`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "book_id": 5,
    "quantity": 2,
    "created_at": "2026-01-20T00:00:00Z"
  },
  {
    "id": 2,
    "customer_id": 1,
    "book_id": 10,
    "quantity": 1,
    "created_at": "2026-01-20T00:05:00Z"
  }
]
```

---

### 2. Add Item to Cart
**POST** `/api/cart/add/`

**Request:**
```json
{
  "customer_id": 1,
  "book_id": 5,
  "quantity": 2
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "customer_id": 1,
  "book_id": 5,
  "quantity": 2,
  "message": "Item added to cart"
}
```

**Business Logic:**
1. Verify customer exists (call Customer Service)
2. Verify book exists and has stock (call Book Service)
3. Check if item already in cart → update quantity
4. Otherwise create new cart item

**Errors:**
- `400 Bad Request` - Customer/Book not found, insufficient stock
- `404 Not Found` - Service unavailable

---

### 3. Update Cart Item Quantity
**PATCH** `/api/cart/items/<item_id>/`

**Request:**
```json
{
  "quantity": 5
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "quantity": 5,
  "message": "Quantity updated"
}
```

---

### 4. Remove Item from Cart
**DELETE** `/api/cart/items/<item_id>/`

**Response:** `204 No Content`

---

### 5. Clear Cart
**DELETE** `/api/cart/<customer_id>/clear/`

**Response:** `204 No Content`

Deletes all items for the customer.

---

### 6. Get Cart Summary (Enhanced)
**GET** `/api/cart/<customer_id>/summary/`

**Response:** `200 OK`
```json
{
  "customer_id": 1,
  "items": [
    {
      "cart_item_id": 1,
      "book": {
        "id": 5,
        "title": "Clean Code",
        "author": "Robert Martin",
        "price": "29.99"
      },
      "quantity": 2,
      "subtotal": "59.98"
    }
  ],
  "total_items": 2,
  "total_price": "59.98"
}
```

**Note:** Aggregate data từ Book Service

## 💻 Code Implementation

### Services (HTTP Clients)

```python
# carts/services.py
import requests
from django.conf import settings

class BookServiceClient:
    """Client to communicate with Book Service"""
    BASE_URL = settings.BOOK_SERVICE_URL
    
    @classmethod
    def get_book(cls, book_id):
        """Get book details"""
        try:
            url = f"{cls.BASE_URL}/api/books/{book_id}/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Book service error: {str(e)}")
    
    @classmethod
    def check_stock(cls, book_id, quantity):
        """Check if book has enough stock"""
        book = cls.get_book(book_id)
        return book.get('stock', 0) >= quantity
    
    @classmethod
    def decrease_stock(cls, book_id, quantity):
        """Decrease book stock"""
        try:
            url = f"{cls.BASE_URL}/api/books/{book_id}/decrease-stock/"
            response = requests.post(url, json={'quantity': quantity}, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to decrease stock: {str(e)}")


class CustomerServiceClient:
    """Client to communicate with Customer Service"""
    BASE_URL = settings.CUSTOMER_SERVICE_URL
    
    @classmethod
    def verify_customer(cls, customer_id):
        """Verify customer exists"""
        try:
            url = f"{cls.BASE_URL}/api/customers/{customer_id}/"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False
```

### Serializers

```python
# carts/serializers.py
from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer"""
    class Meta:
        model = CartItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    """Add to cart request serializer"""
    customer_id = serializers.IntegerField()
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateQuantitySerializer(serializers.Serializer):
    """Update quantity serializer"""
    quantity = serializers.IntegerField(min_value=1)
```

### Views

```python
# carts/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db import transaction
from .models import CartItem
from .serializers import (
    CartItemSerializer, 
    AddToCartSerializer, 
    UpdateQuantitySerializer
)
from .services import BookServiceClient, CustomerServiceClient

class CartViewSet(viewsets.ViewSet):
    """Cart operations"""
    
    def retrieve(self, request, pk=None):
        """Get customer's cart (pk is customer_id)"""
        customer_id = pk
        cart_items = CartItem.objects.filter(customer_id=customer_id)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'])
    def clear(self, request, pk=None):
        """Clear customer's cart"""
        customer_id = pk
        CartItem.objects.filter(customer_id=customer_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get cart summary with book details"""
        customer_id = pk
        cart_items = CartItem.objects.filter(customer_id=customer_id)
        
        items = []
        total_price = 0
        
        for cart_item in cart_items:
            try:
                # Fetch book details from Book Service
                book = BookServiceClient.get_book(cart_item.book_id)
                
                price = float(book['price'])
                subtotal = price * cart_item.quantity
                
                items.append({
                    'cart_item_id': cart_item.id,
                    'book': {
                        'id': book['id'],
                        'title': book['title'],
                        'author': book['author'],
                        'price': book['price']
                    },
                    'quantity': cart_item.quantity,
                    'subtotal': f"{subtotal:.2f}"
                })
                
                total_price += subtotal
                
            except Exception as e:
                # Book might be deleted, skip or handle
                continue
        
        return Response({
            'customer_id': customer_id,
            'items': items,
            'total_items': len(items),
            'total_price': f"{total_price:.2f}"
        })


@api_view(['POST'])
def add_to_cart(request):
    """Add item to cart"""
    serializer = AddToCartSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    customer_id = serializer.validated_data['customer_id']
    book_id = serializer.validated_data['book_id']
    quantity = serializer.validated_data['quantity']
    
    # Verify customer exists
    if not CustomerServiceClient.verify_customer(customer_id):
        return Response(
            {'error': 'Customer not found'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify book exists and has stock
    try:
        book = BookServiceClient.get_book(book_id)
        if book['stock'] < quantity:
            return Response(
                {'error': 'Insufficient stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Add to cart or update quantity
    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(
            customer_id=customer_id,
            book_id=book_id,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Item already in cart, update quantity
            cart_item.quantity += quantity
            cart_item.save()
    
    return Response(
        CartItemSerializer(cart_item).data,
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
    )


@api_view(['PATCH'])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    try:
        cart_item = CartItem.objects.get(id=item_id)
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = UpdateQuantitySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    quantity = serializer.validated_data['quantity']
    
    # Verify stock availability
    if not BookServiceClient.check_stock(cart_item.book_id, quantity):
        return Response(
            {'error': 'Insufficient stock for requested quantity'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    cart_item.quantity = quantity
    cart_item.save()
    
    return Response({
        'id': cart_item.id,
        'quantity': cart_item.quantity,
        'message': 'Quantity updated'
    })


@api_view(['DELETE'])
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except CartItem.DoesNotExist:
        return Response(
            {'error': 'Cart item not found'},
            status=status.HTTP_404_NOT_FOUND
        )
```

### URLs

```python
# carts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/add/', views.add_to_cart, name='add-to-cart'),
    path('cart/items/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    path('cart/items/<int:item_id>/remove/', views.remove_cart_item, name='remove-cart-item'),
]
```

## ⚙️ Settings

```python
# cart_service/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('CART_DB_NAME', 'cart_db'),
        'USER': os.getenv('CART_DB_USER', 'root'),
        'PASSWORD': os.getenv('CART_DB_PASSWORD', ''),
        'HOST': os.getenv('CART_DB_HOST', 'localhost'),
        'PORT': os.getenv('CART_DB_PORT', '3306'),
    }
}

# External service URLs
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://localhost:8001')
BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL', 'http://localhost:8002')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'carts',
]
```

## 🚀 Installation & Setup

```bash
cd cart-service

# Virtual environment
python -m venv venv
venv\Scripts\activate

# Install
pip install -r requirements.txt

# Database
mysql -u root -p -e "CREATE DATABASE cart_db;"

# Migrate
python manage.py makemigrations
python manage.py migrate

# Run
python manage.py runserver 8003
```

**requirements.txt:**
```txt
Django>=4.0
djangorestframework>=3.14
mysqlclient
python-dotenv
requests>=2.28
```

## 🧪 Testing

```bash
# Add to cart
curl -X POST http://localhost:8003/api/cart/add/ \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"book_id":5,"quantity":2}'

# View cart
curl http://localhost:8003/api/cart/1/

# Cart summary
curl http://localhost:8003/api/cart/1/summary/

# Update quantity
curl -X PATCH http://localhost:8003/api/cart/items/1/ \
  -H "Content-Type: application/json" \
  -d '{"quantity":5}'

# Remove item
curl -X DELETE http://localhost:8003/api/cart/items/1/

# Clear cart
curl -X DELETE http://localhost:8003/api/cart/1/clear/
```

## 🔐 Data Integrity Challenges

### Eventual Consistency

Cart Service không có foreign key constraints:
```python
# ❌ Có thể xảy ra:
# - customer_id = 999 (customer không tồn tại)
# - book_id = 888 (book đã bị xóa)

# ✅ Giải pháp:
# - Verify qua API calls trước khi tạo cart item
# - Handle gracefully khi book/customer bị xóa
# - Cleanup orphaned cart items
```

### Handling Deleted References

```python
# Cron job để cleanup orphaned items
@scheduled_task
def cleanup_orphaned_items():
    for cart_item in CartItem.objects.all():
        # Check if customer still exists
        if not CustomerServiceClient.verify_customer(cart_item.customer_id):
            cart_item.delete()
            continue
        
        # Check if book still exists
        try:
            BookServiceClient.get_book(cart_item.book_id)
        except:
            cart_item.delete()
```

## ✅ Best Practices

1. **Timeout Handling**: Set timeouts cho external API calls
2. **Circuit Breaker**: Implement circuit breaker pattern
3. **Caching**: Cache book data để giảm API calls
4. **Idempotency**: Make operations idempotent
5. **Error Handling**: Gracefully handle service failures

---
**Port:** 8003  
**Database:** cart_db (MySQL)  
**Dependencies:** Customer Service, Book Service  
**Domain:** Shopping Cart Management
