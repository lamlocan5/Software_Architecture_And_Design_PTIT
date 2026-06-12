from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests

PRODUCT_SERVICE_URL = "http://product-service:8000"


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
        product_id = data.get("product_id")

        # Fallback mappings for backward compatibility
        if not product_id:
            if book_id and int(book_id) > 0:
                product_id = book_id
            elif clothing_id:
                product_id = clothing_id
            elif electronic_id:
                product_id = electronic_id

        if not product_id:
            return Response({"error": "product_id, book_id, clothing_id hoặc electronic_id là bắt buộc"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_id_int = int(product_id)
        except (ValueError, TypeError):
            return Response({"error": "product_id không hợp lệ"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate with unified product-service
        try:
            r = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id_int}/", timeout=3)
            if r.status_code != 200:
                return Response({"error": "Product not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            pass

        data["product_id"] = product_id_int
        serializer = CartItemSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewCart(APIView):

    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
        except Cart.DoesNotExist:
            return Response([])

        items = CartItem.objects.filter(cart=cart)
        serialized_items = []

        for item in items:
            item_data = CartItemSerializer(item).data
            # Set default backward compatible fields to None or 0
            item_data["book_id"] = 0
            item_data["clothing_id"] = None
            item_data["electronic_id"] = None

            # Fetch product type from product-service to map
            product_id = item.product_id
            if product_id:
                try:
                    r = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}/", timeout=2)
                    if r.status_code == 200:
                        prod = r.json()
                        prod_type = prod.get("product_type")
                        
                        # Set corresponding ID based on type
                        if prod_type == "book" or "title" in prod:
                            item_data["book_id"] = product_id
                        elif prod_type == "clothing" or "clothing_id" in prod:
                            item_data["clothing_id"] = product_id
                        elif prod_type == "electronic" or "electronic_id" in prod:
                            item_data["electronic_id"] = product_id
                except Exception:
                    # Fallback
                    item_data["book_id"] = product_id

            serialized_items.append(item_data)

        return Response(serialized_items)

    def delete(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            CartItem.objects.filter(cart=cart).delete()
            return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)


class CartByCustomer(APIView):
    """Trả về thông tin Cart (bao gồm cart ID) theo customer_id"""

    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)