import uuid
import requests
from django.conf import settings
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer, Cart, CartItem, AuthToken
from .serializers import (
    CustomerSerializer, CustomerRegisterSerializer,
    CustomerLoginSerializer, CartSerializer, CartItemSerializer
)


# ─── Authentication ──────────────────────────────────────────────────────────

@api_view(['POST'])
def customer_register(request):
    """
    POST /customer/register/  — Đăng ký tài khoản mới
    """
    serializer = CustomerRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    if Customer.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if Customer.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    customer = Customer(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name', ''),
        phone=data.get('phone', ''),
    )
    customer.set_password(data['password'])
    customer.save()

    # Auto-create cart for customer
    Cart.objects.create(customer=customer)

    return Response({
        'message': 'Registration successful',
        'customer': CustomerSerializer(customer).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def customer_login(request):
    """
    POST /customer/login/  — Đăng nhập, trả về token
    """
    serializer = CustomerLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        customer = Customer.objects.get(username=data['username'])
    except Customer.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not customer.check_password(data['password']):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token = str(uuid.uuid4())
    AuthToken.objects.create(key=token, customer=customer)

    return Response({
        'token': token,
        'customer': CustomerSerializer(customer).data
    })


def _get_customer_from_token(token):
    """Helper: lấy customer từ token, trả về (customer, error_response)"""
    if not token:
        return None, Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        at = AuthToken.objects.select_related('customer').get(key=token)
        return at.customer, None
    except AuthToken.DoesNotExist:
        return None, Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)


# ─── Token Verification (dùng bửi order-service) ───────────────────────────────

@api_view(['GET'])
def verify_token(request):
    """
    GET /customer/verify/?token=<token>
    Dùng bởi các service khác để xác thực token và lấy thông tin customer
    """
    token = request.query_params.get('token')
    customer, error = _get_customer_from_token(token)
    if error:
        return error
    return Response({
        'valid': True,
        'customer_id': customer.id,
        'username': customer.username,
        'email': customer.email,
        'full_name': customer.full_name,
        'created_at': customer.created_at.isoformat() if customer.created_at else None,
    })


# ─── Search ───────────────────────────────────────────────────────────────────

@api_view(['GET'])
def search_products(request):
    """
    GET /customer/search/?q=<query>&type=laptop|mobile|all
    Tìm kiếm sản phẩm từ laptop-service và mobile-service
    """
    query = request.query_params.get('q', '')
    search_type = request.query_params.get('type', 'all')
    results = []

    try:
        if search_type in ['laptop', 'all']:
            url = f"{settings.LAPTOP_SERVICE_URL}/laptops/search/?q={query}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                laptops = data.get('results', data) if isinstance(data, dict) else data
                for item in laptops:
                    item['product_type'] = 'laptop'
                results.extend(laptops)

        if search_type in ['mobile', 'all']:
            url = f"{settings.MOBILE_SERVICE_URL}/mobiles/search/?q={query}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                mobiles = data.get('results', data) if isinstance(data, dict) else data
                for item in mobiles:
                    item['product_type'] = 'mobile'
                results.extend(mobiles)

    except requests.RequestException as e:
        return Response({'error': f'Search service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response({
        'query': query,
        'count': len(results),
        'results': results
    })


# ─── Cart ─────────────────────────────────────────────────────────────────────

@api_view(['GET'])
def get_cart(request):
    """
    GET /customer/cart/?token=<token>  — Xem giỏ hàng
    """
    token = request.query_params.get('token')
    customer, error = _get_customer_from_token(token)
    if error:
        return error

    cart, _ = Cart.objects.get_or_create(customer=customer)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
def add_to_cart(request):
    """
    POST /customer/cart/add/
    Body: { "token": "...", "product_id": 1, "product_type": "laptop"|"mobile",
            "product_name": "...", "price": 999.99, "quantity": 1 }
    """
    token = request.data.get('token')
    customer, error = _get_customer_from_token(token)
    if error:
        return error

    cart, _ = Cart.objects.get_or_create(customer=customer)

    product_id = request.data.get('product_id')
    product_type = request.data.get('product_type')
    product_name = request.data.get('product_name', '')
    price = request.data.get('price')
    quantity = int(request.data.get('quantity', 1))

    if not all([product_id, product_type, price]):
        return Response({'error': 'product_id, product_type, and price are required'}, status=status.HTTP_400_BAD_REQUEST)

    if product_type not in ['laptop', 'mobile']:
        return Response({'error': 'product_type must be "laptop" or "mobile"'}, status=status.HTTP_400_BAD_REQUEST)

    # Upsert cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id,
        product_type=product_type,
        defaults={'product_name': product_name, 'price': price, 'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    serializer = CartSerializer(cart)
    return Response({
        'message': 'Added to cart',
        'cart': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def remove_from_cart(request, item_id):
    """
    DELETE /customer/cart/remove/<item_id>/?token=<token>  — Xóa item khỏi giỏ hàng
    """
    token = request.query_params.get('token')
    customer, error = _get_customer_from_token(token)
    if error:
        return error

    try:
        cart = Cart.objects.get(customer=customer)
        item = CartItem.objects.get(id=item_id, cart=cart)
        item.delete()
        return Response({'message': 'Item removed from cart'})
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def clear_cart(request):
    """
    DELETE /customer/cart/clear/?token=<token>  — Xóa toàn bộ giỏ hàng
    """
    token = request.query_params.get('token')
    customer, error = _get_customer_from_token(token)
    if error:
        return error

    try:
        cart = Cart.objects.get(customer=customer)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'})
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
