# Frontend Gateway Service

## 📋 Tổng quan

Frontend Gateway Service là **API Gateway** và **User Interface** cho Microservices Architecture. Service này không có database riêng mà aggregate data từ các backend services khác.

## 🎯 Trách nhiệm

- 🌐 Cung cấp giao diện web (HTML/CSS/JS)
- 🔀 Routing requests đến các microservices
- 📊 Aggregate và combine data từ nhiều services
- 🔐 Quản lý session và authentication state
- 🎨 Render templates với data từ APIs

## 🏗️ Kiến trúc

```
┌─────────────────────────────────────┐
│      Frontend Gateway (8000)        │
│                                     │
│  ┌──────────┐      ┌─────────┐    │
│  │Templates │      │  Views  │    │
│  │  Layer   │◄─────┤  Layer  │    │
│  └──────────┘      └────┬────┘    │
│                          │          │
│                    ┌─────▼────┐    │
│                    │ HTTP     │    │
│                    │ Clients  │    │
│                    └────┬─────┘    │
└─────────────────────────┼──────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
   ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
   │ Customer    │ │   Book    │ │   Cart      │
   │ Service     │ │  Service  │ │  Service    │
   │  :8001      │ │   :8002   │ │   :8003     │
   └─────────────┘ └───────────┘ └─────────────┘
```

## 📁 Cấu trúc

```
frontend/
├── manage.py                   # Django management
├── requirements.txt            # Dependencies
│
├── frontend_service/          # Django project config
│   ├── __init__.py
│   ├── settings.py           # Settings (no database!)
│   ├── urls.py               # Main URL config
│   ├── wsgi.py
│   └── asgi.py
│
├── web/                       # Main application
│   ├── __init__.py
│   ├── views.py              # View controllers
│   ├── urls.py               # URL routes
│   └── services.py           # HTTP clients for APIs
│
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── home.html             # Homepage
│   ├── books/
│   │   ├── list.html         # Book listing
│   │   └── detail.html       # Book details
│   ├── accounts/
│   │   ├── login.html        # Login page
│   │   └── register.html     # Register page
│   └── cart/
│       └── view.html         # Shopping cart
│
└── static/                    # CSS, JS, images
    └── css/
        └── styles.css
```

## 🔗 Service URLs Configuration

File `.env` hoặc trong `settings.py`:
```python
# Backend service URLs
CUSTOMER_SERVICE_URL = 'http://localhost:8001'
BOOK_SERVICE_URL = 'http://localhost:8002'
CART_SERVICE_URL = 'http://localhost:8003'
```

## 🚀 URL Routes

| URL | View | Chức năng |
|-----|------|-----------|
| `/` | `home_view` | Trang chủ |
| `/register/` | `register_view` | Đăng ký tài khoản |
| `/login/` | `login_view` | Đăng nhập |
| `/logout/` | `logout_view` | Đăng xuất |
| `/books/` | `book_list_view` | Danh sách sách |
| `/books/<id>/` | `book_detail_view` | Chi tiết sách |
| `/cart/` | `cart_view` | Xem giỏ hàng |
| `/cart/add/<book_id>/` | `add_to_cart_view` | Thêm vào giỏ |
| `/cart/remove/<item_id>/` | `remove_from_cart_view` | Xóa khỏi giỏ |

## 💻 Example Code

### services.py - HTTP Clients

```python
import requests
from django.conf import settings

class CustomerServiceClient:
    BASE_URL = settings.CUSTOMER_SERVICE_URL
    
    @classmethod
    def register(cls, username, email, password):
        """Register new customer"""
        url = f"{cls.BASE_URL}/api/register/"
        data = {
            'username': username,
            'email': email,
            'password': password
        }
        response = requests.post(url, json=data)
        return response.json()
    
    @classmethod
    def login(cls, username, password):
        """Login customer"""
        url = f"{cls.BASE_URL}/api/login/"
        data = {'username': username, 'password': password}
        response = requests.post(url, json=data)
        return response.json()
    
    @classmethod
    def get_customer(cls, customer_id):
        """Get customer details"""
        url = f"{cls.BASE_URL}/api/customers/{customer_id}/"
        response = requests.get(url)
        return response.json()


class BookServiceClient:
    BASE_URL = settings.BOOK_SERVICE_URL
    
    @classmethod
    def get_all_books(cls):
        """Get all books"""
        url = f"{cls.BASE_URL}/api/books/"
        response = requests.get(url)
        return response.json()
    
    @classmethod
    def get_book(cls, book_id):
        """Get book details"""
        url = f"{cls.BASE_URL}/api/books/{book_id}/"
        response = requests.get(url)
        return response.json()


class CartServiceClient:
    BASE_URL = settings.CART_SERVICE_URL
    
    @classmethod
    def get_cart(cls, customer_id):
        """Get customer's cart"""
        url = f"{cls.BASE_URL}/api/cart/{customer_id}/"
        response = requests.get(url)
        return response.json()
    
    @classmethod
    def add_to_cart(cls, customer_id, book_id, quantity=1):
        """Add item to cart"""
        url = f"{cls.BASE_URL}/api/cart/add/"
        data = {
            'customer_id': customer_id,
            'book_id': book_id,
            'quantity': quantity
        }
        response = requests.post(url, json=data)
        return response.json()
    
    @classmethod
    def remove_from_cart(cls, item_id):
        """Remove item from cart"""
        url = f"{cls.BASE_URL}/api/cart/items/{item_id}/"
        response = requests.delete(url)
        return response.status_code == 204
```

### views.py - View Controllers

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from .services import CustomerServiceClient, BookServiceClient, CartServiceClient

def home_view(request):
    """Homepage"""
    return render(request, 'home.html')


def register_view(request):
    """Register new customer"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            result = CustomerServiceClient.register(username, email, password)
            messages.success(request, 'Registration successful!')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """Login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            result = CustomerServiceClient.login(username, password)
            # Store customer_id in session
            request.session['customer_id'] = result['customer_id']
            request.session['username'] = result['username']
            messages.success(request, 'Login successful!')
            return redirect('book_list')
        except Exception as e:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'accounts/login.html')


def book_list_view(request):
    """List all books"""
    try:
        books = BookServiceClient.get_all_books()
        return render(request, 'books/list.html', {'books': books})
    except Exception as e:
        messages.error(request, 'Error loading books')
        return render(request, 'books/list.html', {'books': []})


def book_detail_view(request, book_id):
    """Book details"""
    try:
        book = BookServiceClient.get_book(book_id)
        return render(request, 'books/detail.html', {'book': book})
    except Exception as e:
        messages.error(request, 'Book not found')
        return redirect('book_list')


def cart_view(request):
    """View shopping cart"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    try:
        # Get cart items
        cart_items = CartServiceClient.get_cart(customer_id)
        
        # Enrich with book details
        for item in cart_items:
            book = BookServiceClient.get_book(item['book_id'])
            item['book'] = book
            item['subtotal'] = float(book['price']) * item['quantity']
        
        # Calculate total
        total = sum(item['subtotal'] for item in cart_items)
        
        return render(request, 'cart/view.html', {
            'cart_items': cart_items,
            'total': total
        })
    except Exception as e:
        messages.error(request, 'Error loading cart')
        return render(request, 'cart/view.html', {'cart_items': []})


def add_to_cart_view(request, book_id):
    """Add book to cart"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')
    
    try:
        CartServiceClient.add_to_cart(customer_id, book_id, quantity=1)
        messages.success(request, 'Book added to cart!')
    except Exception as e:
        messages.error(request, 'Error adding to cart')
    
    return redirect('cart')
```

## 🎨 Templates

### base.html
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Book Store{% endblock %}</title>
    <link rel="stylesheet" href="{% static 'css/styles.css' %}">
</head>
<body>
    <nav>
        <a href="{% url 'home' %}">Home</a>
        <a href="{% url 'book_list' %}">Books</a>
        
        {% if request.session.customer_id %}
            <a href="{% url 'cart' %}">Cart</a>
            <span>Hello, {{ request.session.username }}!</span>
            <a href="{% url 'logout' %}">Logout</a>
        {% else %}
            <a href="{% url 'login' %}">Login</a>
            <a href="{% url 'register' %}">Register</a>
        {% endif %}
    </nav>
    
    {% if messages %}
        {% for message in messages %}
            <div class="alert">{{ message }}</div>
        {% endfor %}
    {% endif %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### books/list.html
```html
{% extends 'base.html' %}

{% block title %}Books{% endblock %}

{% block content %}
<h1>Available Books</h1>

<div class="book-grid">
    {% for book in books %}
    <div class="book-card">
        <h3>{{ book.title }}</h3>
        <p>by {{ book.author }}</p>
        <p class="price">${{ book.price }}</p>
        <p>Stock: {{ book.stock }}</p>
        <a href="{% url 'book_detail' book.id %}">View Details</a>
        
        {% if book.stock > 0 %}
            <a href="{% url 'add_to_cart' book.id %}">Add to Cart</a>
        {% else %}
            <span>Out of Stock</span>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}
```

## 🔐 Session Management

Frontend service quản lý session cho authentication:

```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True

# Store customer_id in session after login
request.session['customer_id'] = customer_id
request.session['username'] = username

# Check authentication in views
if not request.session.get('customer_id'):
    return redirect('login')
```

## 🚀 Installation

```bash
cd frontend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server (no migrations needed!)
python manage.py runserver 8000
```

### requirements.txt
```txt
Django>=4.0
requests>=2.28
python-dotenv
```

## ⚙️ Settings Configuration

```python
# settings.py

# No database for frontend!
DATABASES = {}

# Service URLs
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://localhost:8001')
BOOK_SERVICE_URL = os.getenv('BOOK_SERVICE_URL', 'http://localhost:8002')
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://localhost:8003')

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

## 🐛 Error Handling

```python
import requests
from django.contrib import messages

def safe_api_call(func):
    """Decorator for safe API calls"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError:
            raise Exception("Service unavailable")
        except requests.Timeout:
            raise Exception("Request timeout")
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")
    return wrapper

@safe_api_call
def get_books():
    response = requests.get(f"{BOOK_SERVICE_URL}/api/books/")
    response.raise_for_status()
    return response.json()
```

## ✅ Ưu điểm

- ✅ Single entry point cho users
- ✅ Centralized authentication
- ✅ Easy to add caching layer
- ✅ Can aggregate data from multiple services
- ✅ Simplified client-side logic

## ❌ Challenges

- ❌ Single point of failure
- ❌ Potential bottleneck
- ❌ Tightly coupled với backend APIs
- ❌ Network latency khi aggregate data

## 📚 Best Practices

1. **Caching**: Cache API responses để giảm latency
2. **Circuit Breaker**: Handle service failures gracefully
3. **Timeout**: Set reasonable timeouts cho API calls
4. **Retry**: Implement retry logic
5. **Logging**: Log all API calls để debug

---
**Port:** 8000  
**Database:** None  
**Dependencies:** Customer, Book, Cart services  
**Role:** API Gateway + UI
