from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Payment
from .serializers import PaymentSerializer


class PaymentList(APIView):
    def get(self, request):
        payments = Payment.objects.all().order_by('-created_at')
        return Response(PaymentSerializer(payments, many=True).data)


class PaymentCreate(APIView):
    def post(self, request):
        for f in ['order_id', 'customer_id', 'amount']:
            if request.data.get(f) in [None, '']:
                return Response({"error": f"{f} là bắt buộc"}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            order_id=request.data.get('order_id'),
            customer_id=request.data.get('customer_id'),
            amount=request.data.get('amount', 0),
            method=request.data.get('method', 'cod') or 'cod',
            provider=request.data.get('provider', '') or '',
            transaction_id=request.data.get('transaction_id', '') or '',
            status='initiated',
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentDetail(APIView):
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({"error": "Không tìm thấy payment"}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)


class PaymentStatusUpdate(APIView):
    VALID_STATUSES = ['initiated', 'paid', 'failed', 'refunded', 'cancelled']

    def patch(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({"error": "Không tìm thấy payment"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in self.VALID_STATUSES:
            return Response(
                {"error": f"Trạng thái không hợp lệ. Chọn: {self.VALID_STATUSES}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = new_status
        payment.save()

        # Publish payment_processed event asynchronously for order-service and notification-service
        try:
            from .event_broker import publish_event
            publish_event('payment_processed', {
                'payment_id': payment.id,
                'order_id': payment.order_id,
                'customer_id': payment.customer_id,
                'amount': float(payment.amount),
                'status': payment.status
            })
        except Exception as e:
            print(f"[Payment Service] Failed to publish payment_processed event: {e}")

        return Response(PaymentSerializer(payment).data)


class OrderPayments(APIView):
    def get(self, request, order_id):
        payments = Payment.objects.filter(order_id=order_id).order_by('-created_at')
        return Response(PaymentSerializer(payments, many=True).data)


class CustomerPayments(APIView):
    def get(self, request, customer_id):
        payments = Payment.objects.filter(customer_id=customer_id).order_by('-created_at')
        return Response(PaymentSerializer(payments, many=True).data)

