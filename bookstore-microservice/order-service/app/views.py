from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderDetailSerializer


class OrderList(APIView):
    """GET tất cả đơn hàng"""
    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderCreate(APIView):
    """POST tạo đơn hàng mới (kèm items)"""
    def post(self, request):
        customer_id  = request.data.get('customer_id')
        total_amount = request.data.get('total_amount', 0)
        items        = request.data.get('items', [])

        if not customer_id or not items:
            return Response(
                {"error": "customer_id và items là bắt buộc"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(
            customer_id=customer_id,
            total_amount=total_amount,
            status='pending',
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                book_id=item['book_id'],
                quantity=item['quantity'],
                price_at_order=item['price_at_order'],
            )

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetail(APIView):
    """GET chi tiết đơn hàng (kèm items)"""
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


class OrderStatusUpdate(APIView):
    """PATCH cập nhật trạng thái đơn hàng"""
    VALID_STATUSES = ['pending', 'confirmed', 'shipping', 'delivered', 'cancelled']

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Không tìm thấy đơn hàng"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in self.VALID_STATUSES:
            return Response(
                {"error": f"Trạng thái không hợp lệ. Chọn: {self.VALID_STATUSES}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class CustomerOrders(APIView):
    """GET danh sách đơn hàng theo customer_id"""
    def get(self, request, customer_id):
        orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
        serializer = OrderDetailSerializer(orders, many=True)
        return Response(serializer.data)
