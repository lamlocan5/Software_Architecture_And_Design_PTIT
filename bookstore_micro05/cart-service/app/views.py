from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

# ---- Chạy bằng Docker (docker compose up) ----
BOOK_SERVICE_URL = "http://book-service:8000"

# ---- Chạy KHÔNG dùng Docker (python manage.py runserver) ----
# BOOK_SERVICE_URL = "http://localhost:8002"


class CartCreate(APIView):
    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


class AddCartItem(APIView):
    def post(self, request):
        book_id = request.data.get("book_id")
        # Kiểm tra book tồn tại qua book-service (nếu lỗi thì bỏ qua)
        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=3)
            if r.status_code == 200:
                books = r.json()
                if isinstance(books, list) and not any(b["id"] == book_id for b in books):
                    return Response({"error": "Book not found"}, status=404)
        except Exception:
            pass  # Nếu book-service không phản hồi, vẫn cho thêm vào giỏ

        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ViewCart(APIView):
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)
