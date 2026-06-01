import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer


def _verify_token(token):
    """
    Gọi customer-service /customer/verify/ để xác minh token.
    Trả về (customer_data, None) nếu hợp lệ, hoặc (None, error_response).
    """
    if not token:
        return None, Response({'error': 'Token là bắt buộc'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        url = f"{settings.CUSTOMER_SERVICE_URL}/customer/verify/?token={token}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data, None
        elif resp.status_code == 401:
            return None, Response({'error': 'Token không hợp lệ hoặc đã hết hạn'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return None, Response({'error': 'Không thể xác thực người dùng'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    except requests.RequestException as e:
        return None, Response({'error': f'Customer service không khả dụng: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# ─── Tạo đơn hàng ─────────────────────────────────────────────────────────────

@api_view(['POST'])
def create_order(request):
    """
    POST /orders/create/
    Body: {
        "token": "...",
        "customer_name": "...",
        "customer_email": "...",   (tùy chọn)
        "shipping_address": "...", (tùy chọn)
        "note": "...",             (tùy chọn)
        "items": [
            {"product_id": 1, "product_type": "laptop", "product_name": "...", "price": 999.99, "quantity": 2},
            ...
        ]
    }
    """
    token = request.data.get('token')
    cart_data, error = _verify_token(token)
    if error:
        return error

    # Lấy customer_id từ cart data của customer-service
    customer_id = cart_data.get('customer_id', 0)

    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data
    items_data = validated.get('items', [])

    # Validate items
    for item in items_data:
        if not all(k in item for k in ['product_id', 'product_type', 'product_name', 'price', 'quantity']):
            return Response(
                {'error': 'Mỗi item cần có: product_id, product_type, product_name, price, quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if item.get('product_type') not in ['laptop', 'mobile']:
            return Response({'error': 'product_type phải là "laptop" hoặc "mobile"'}, status=status.HTTP_400_BAD_REQUEST)
        if int(item.get('quantity', 0)) < 1:
            return Response({'error': 'Số lượng phải >= 1'}, status=status.HTTP_400_BAD_REQUEST)

    # Tạo Order
    order = Order.objects.create(
        customer_id=customer_id,
        customer_name=validated['customer_name'],
        customer_email=validated.get('customer_email', ''),
        shipping_address=validated.get('shipping_address', ''),
        note=validated.get('note', ''),
        status='pending',
    )

    # Tạo OrderItems
    total = 0
    for item in items_data:
        qty = int(item['quantity'])
        price = float(item['price'])
        OrderItem.objects.create(
            order=order,
            product_id=item['product_id'],
            product_type=item['product_type'],
            product_name=item['product_name'],
            price=price,
            quantity=qty,
        )
        total += price * qty

    order.total_price = total
    order.save(update_fields=['total_price'])

    return Response({
        'message': 'Đặt hàng thành công! 🎉',
        'order': OrderSerializer(order).data
    }, status=status.HTTP_201_CREATED)


# ─── Lịch sử đơn hàng ─────────────────────────────────────────────────────────

@api_view(['GET'])
def list_orders(request):
    """
    GET /orders/?token=<token>
    Trả về danh sách đơn hàng của customer
    """
    token = request.query_params.get('token')
    cart_data, error = _verify_token(token)
    if error:
        return error

    customer_id = cart_data.get('customer_id', 0)
    orders = Order.objects.filter(customer_id=customer_id).prefetch_related('items')
    serializer = OrderSerializer(orders, many=True)
    return Response({
        'count': orders.count(),
        'orders': serializer.data
    })


# ─── Chi tiết đơn hàng ────────────────────────────────────────────────────────

@api_view(['GET'])
def order_detail(request, order_id):
    """
    GET /orders/<order_id>/?token=<token>
    Trả về chi tiết 1 đơn hàng của customer
    """
    token = request.query_params.get('token')
    cart_data, error = _verify_token(token)
    if error:
        return error

    customer_id = cart_data.get('customer_id', 0)

    try:
        order = Order.objects.prefetch_related('items').get(id=order_id, customer_id=customer_id)
    except Order.DoesNotExist:
        return Response({'error': 'Đơn hàng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

    return Response(OrderSerializer(order).data)


# ─── Cập nhật trạng thái (nội bộ) ─────────────────────────────────────────────

@api_view(['PATCH'])
def update_order_status(request, order_id):
    """
    PATCH /orders/<order_id>/status/
    Body: { "status": "confirmed" | "shipping" | "delivered" | "cancelled" }
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Đơn hàng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response(
            {'error': f'Trạng thái không hợp lệ. Chọn một trong: {valid_statuses}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    return Response({'message': 'Cập nhật trạng thái thành công', 'order': OrderSerializer(order).data})
