from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"
CLOTHE_SERVICE_URL = "http://clothe-service:8000"
ELECTRONIC_SERVICE_URL = "http://electronic-service:8000"


class CartCreate(APIView):

    def post(self, request):

        serializer = CartSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


class AddCartItem(APIView):

    def post(self, request):

        data = request.data.copy()
        book_id = data.get("book_id")
        clothing_id = data.get("clothing_id")
        electronic_id = data.get("electronic_id")

        if not book_id and not clothing_id and not electronic_id:
            return Response({"error": "book_id, clothing_id hoặc electronic_id là bắt buộc"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate book nếu có
        if book_id:
            try:
                book_id_int = int(book_id)
            except (ValueError, TypeError):
                return Response({"error": "book_id không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
            r = requests.get(f"{BOOK_SERVICE_URL}/books/")
            books = r.json()
            if not any(b.get("id") == book_id_int for b in books if isinstance(b, dict)):
                return Response({"error": "Book not found"}, status=status.HTTP_400_BAD_REQUEST)
            data["book_id"] = book_id_int
        else:
            # DB hiện vẫn có ràng buộc NOT NULL với book_id trên một số môi trường,
            # nên dùng 0 làm giá trị "không phải sách" thay vì NULL.
            data["book_id"] = 0

        # Validate clothing nếu có
        if clothing_id:
            try:
                clothing_id_int = int(clothing_id)
            except (ValueError, TypeError):
                return Response({"error": "clothing_id không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                r = requests.get(f"{CLOTHE_SERVICE_URL}/clothes/")
                clothes = r.json()
            except Exception:
                clothes = []
            if not any(c.get("id") == clothing_id_int for c in clothes if isinstance(c, dict)):
                return Response({"error": "Clothing not found"}, status=status.HTTP_400_BAD_REQUEST)
            data["clothing_id"] = clothing_id_int
        else:
            data["clothing_id"] = None

        # Validate electronic nếu có
        if electronic_id:
            try:
                electronic_id_int = int(electronic_id)
            except (ValueError, TypeError):
                return Response({"error": "electronic_id không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                r = requests.get(f"{ELECTRONIC_SERVICE_URL}/electronics/")
                electronics = r.json()
            except Exception:
                electronics = []
            if not any(e.get("id") == electronic_id_int for e in electronics if isinstance(e, dict)):
                return Response({"error": "Electronic not found"}, status=status.HTTP_400_BAD_REQUEST)
            data["electronic_id"] = electronic_id_int
        else:
            data["electronic_id"] = None

        serializer = CartItemSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)


class ViewCart(APIView):

    def get(self, request, customer_id):

        cart = Cart.objects.get(customer_id=customer_id)

        items = CartItem.objects.filter(cart=cart)

        serializer = CartItemSerializer(items, many=True)

        return Response(serializer.data)


class CartByCustomer(APIView):
    """Trả về thông tin Cart (bao gồm cart ID) theo customer_id"""

    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)