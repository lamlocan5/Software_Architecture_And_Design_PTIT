from django.shortcuts import render
import requests

# ---- Chạy bằng Docker (docker compose up) ----
BOOK_SERVICE_URL = "http://book-service:8000"
CART_SERVICE_URL = "http://cart-service:8000"

# ---- Chạy KHÔNG dùng Docker (python manage.py runserver) ----
# BOOK_SERVICE_URL = "http://localhost:8002"
# CART_SERVICE_URL = "http://localhost:8003"


def book_list(request):
    try:
        r = requests.get(f"{BOOK_SERVICE_URL}/books/")
        books = r.json() if r.status_code == 200 else []
    except Exception:
        books = []
    return render(request, "books.html", {"books": books})


def view_cart(request, customer_id):
    try:
        r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
        items = r.json() if r.status_code == 200 else []
        # Nếu trả về dict (ví dụ {"error": ...}) thì dùng list rỗng
        if isinstance(items, dict):
            items = []
    except Exception:
        items = []
    return render(request, "cart.html", {"items": items})
