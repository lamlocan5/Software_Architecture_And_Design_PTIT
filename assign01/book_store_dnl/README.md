# Book Store Application

This project contains three versions of a Book Store application, demonstrating the evolution from a Monolithic architecture to Microservices.

## Project Structure

- **Monolithic Django**: The initial monolithic implementation using Django. All features (Books, Customers, Cart) are in a single project.
- **Clean Architecture Django**: A structured version of the monolith following Clean Architecture principles.
- **Microservices Django**: A microservices implementation splitting the domains into separate services.

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server (running at `localhost:3306`, user `root`, no password, or configure `.env` files)

### 1. Monolith
(Legacy version)
```bash
cd Monolithic Django
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Version B (Clean Architecture)
```bash
cd Clean Architecture Django
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. Version C (Microservices)

#### Running Services

**Frontend Gateway** (Port 8000) - The User Interface for Microservices.
```bash
cd Microservices Django/frontend
pip install -r requirements.txt
python manage.py runserver 8000
```

**Book Service** (Port 8002) - Manages book catalog and stock.
```bash
cd Microservices Django/book-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002
```

**Customer Service** (Port 8001) - Manages customer registration and auth.
```bash
cd Microservices Django/customer-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001
```

**Cart Service** (Port 8003) - Manages shopping carts.
```bash
cd Microservices Django/cart-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8003
```

## API Endpoints (Version C)

### Book Service (:8002)
- `GET /api/books/`: List all books
- `GET /api/books/<id>/`: Get book details
- `PATCH /api/books/<id>/stock/`: Update stock

### Customer Service (:8001)
- `POST /api/register/`: Register new customer
- `POST /api/login/`: Login
- `GET /api/customers/<id>/`: Get profile

### Cart Service (:8003)
- `POST /api/cart/add/`: Add item to cart
- `GET /api/cart/<customer_id>/`: View cart
- `DELETE /api/cart/items/<id>/`: Remove item
