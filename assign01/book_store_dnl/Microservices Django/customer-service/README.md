# Customer Service

## 📋 Tổng quan

Customer Service là microservice chịu trách nhiệm quản lý thông tin khách hàng và xác thực (authentication). Service này hoạt động độc lập với database riêng và expose REST APIs.

## 🎯 Trách nhiệm

- 👤 Quản lý thông tin khách hàng
- 🔐 Authentication (Register/Login)
- 📝 CRUD operations cho Customer
- 🔑 Password hashing và security
- 📊 Provide customer data cho các services khác

## 🏗️ Kiến trúc

```
┌─────────────────────────────────┐
│   Customer Service (:8001)      │
│                                 │
│  ┌─────────────────────────┐   │
│  │    REST API Layer       │   │
│  │  (views, serializers)   │   │
│  └───────────┬─────────────┘   │
│              │                  │
│  ┌───────────▼─────────────┐   │
│  │   Business Logic Layer  │   │
│  └───────────┬─────────────┘   │
│              │                  │
│  ┌───────────▼─────────────┐   │
│  │    Django ORM Models    │   │
│  └───────────┬─────────────┘   │
└──────────────┼──────────────────┘
               │
      ┌────────▼────────┐
      │  customer_db    │
      │   (MySQL)       │
      └─────────────────┘
```

## 📁 Cấu trúc

```
customer-service/
├── manage.py                      # Django management
├── requirements.txt               # Dependencies
│
├── customer_service/             # Django project
│   ├── __init__.py
│   ├── settings.py              # Database: customer_db
│   ├── urls.py                  # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
│
└── customers/                    # Django app
    ├── __init__.py
    ├── models.py                # Customer model
    ├── views.py                 # API views
    ├── serializers.py           # DRF serializers
    ├── urls.py                  # App URL routes
    ├── admin.py                 # Admin config
    └── migrations/              # Database migrations
        └── ...
```

## 🗃️ Database Schema

**Database:** `customer_db`

**Table:** `customers`

```sql
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

## 💻 Models

```python
# customers/models.py
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Customer(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)
```

## 📡 API Endpoints

### 1. Register Customer
**POST** `/api/register/`

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2026-01-20T00:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Validation error (username exists, invalid email, etc.)

---

### 2. Login Customer
**POST** `/api/login/`

**Request:**
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response:** `200 OK`
```json
{
  "customer_id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "message": "Login successful"
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials

---

### 3. Get Customer Details
**GET** `/api/customers/<id>/`

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2026-01-20T00:00:00Z",
  "updated_at": "2026-01-20T00:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Customer doesn't exist

---

### 4. Update Customer
**PUT/PATCH** `/api/customers/<id>/`

**Request:**
```json
{
  "first_name": "Johnny",
  "email": "johnny@example.com"
}
```

**Response:** `200 OK`

---

### 5. Delete Customer
**DELETE** `/api/customers/<id>/`

**Response:** `204 No Content`

---

### 6. List All Customers (Admin)
**GET** `/api/customers/`

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    ...
  },
  ...
]
```

## 💻 Code Implementation

### Serializers

```python
# customers/serializers.py
from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    """Full customer serializer"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'password', 
                  'first_name', 'last_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Hash password on create"""
        password = validated_data.pop('password')
        customer = Customer(**validated_data)
        customer.set_password(password)
        customer.save()
        return customer


class LoginSerializer(serializers.Serializer):
    """Login request serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
```

### Views

```python
# customers/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer, LoginSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    """CRUD operations for customers"""
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


@api_view(['POST'])
def register_view(request):
    """Register new customer"""
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        return Response(
            CustomerSerializer(customer).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    """Login customer"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    try:
        customer = Customer.objects.get(username=username)
        if customer.check_password(password):
            return Response({
                'customer_id': customer.id,
                'username': customer.username,
                'email': customer.email,
                'message': 'Login successful'
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
```

### URLs

```python
# customers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
]
```

```python
# customer_service/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('customers.urls')),
]
```

## ⚙️ Settings

```python
# customer_service/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('CUSTOMER_DB_NAME', 'customer_db'),
        'USER': os.getenv('CUSTOMER_DB_USER', 'root'),
        'PASSWORD': os.getenv('CUSTOMER_DB_PASSWORD', ''),
        'HOST': os.getenv('CUSTOMER_DB_HOST', 'localhost'),
        'PORT': os.getenv('CUSTOMER_DB_PORT', '3306'),
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
    'customers',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
}
```

## 🚀 Installation & Setup

### Step 1: Create Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE customer_db;
```

### Step 2: Install Dependencies

```bash
cd customer-service

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install packages
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

Create `.env` file:
```env
CUSTOMER_DB_NAME=customer_db
CUSTOMER_DB_USER=root
CUSTOMER_DB_PASSWORD=
CUSTOMER_DB_HOST=localhost
CUSTOMER_DB_PORT=3306
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Step 4: Migrate Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 6: Run Server

```bash
python manage.py runserver 8001
```

Service available at: **http://localhost:8001**

## 🧪 Testing APIs

### Using cURL

**Register:**
```bash
curl -X POST http://localhost:8001/api/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"john\",\"email\":\"john@email.com\",\"password\":\"pass123\"}"
```

**Login:**
```bash
curl -X POST http://localhost:8001/api/login/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"john\",\"password\":\"pass123\"}"
```

**Get Customer:**
```bash
curl http://localhost:8001/api/customers/1/
```

### Using Python requests

```python
import requests

# Register
response = requests.post('http://localhost:8001/api/register/', json={
    'username': 'john_doe',
    'email': 'john@example.com',
    'password': 'secure123'
})
print(response.json())

# Login
response = requests.post('http://localhost:8001/api/login/', json={
    'username': 'john_doe',
    'password': 'secure123'
})
customer_data = response.json()
print(customer_data)

# Get customer
customer_id = customer_data['customer_id']
response = requests.get(f'http://localhost:8001/api/customers/{customer_id}/')
print(response.json())
```

## 🔐 Security Considerations

### Password Hashing
```python
from django.contrib.auth.hashers import make_password, check_password

# Hash password before saving
hashed = make_password('raw_password')

# Verify password
is_valid = check_password('raw_password', hashed)
```

### Input Validation
- Username: alphanumeric, unique
- Email: valid email format, unique
- Password: minimum length (implement in serializer)

### Best Practices
1. ✅ Never return password in API response
2. ✅ Use HTTPS in production
3. ✅ Implement rate limiting
4. ✅ Add JWT token authentication
5. ✅ Validate all inputs

## 🐛 Troubleshooting

### Database connection error
```bash
# Check MySQL is running
mysql -u root -p -e "SHOW DATABASES;"

# Verify .env configuration
cat .env
```

### Migration issues
```bash
# Reset migrations
python manage.py migrate customers zero
python manage.py migrate
```

### Port already in use
```bash
# Run on different port
python manage.py runserver 8011
```

## 📊 Monitoring

### Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'customer_service.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Health Check Endpoint
```python
@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy', 'service': 'customer-service'})
```

## 📚 Future Enhancements

- [ ] JWT token authentication
- [ ] Email verification
- [ ] Password reset functionality
- [ ] OAuth2 integration
- [ ] Role-based access control (RBAC)
- [ ] Two-factor authentication (2FA)

---
**Port:** 8001  
**Database:** customer_db (MySQL)  
**Framework:** Django REST Framework  
**Domain:** Customer & Authentication
