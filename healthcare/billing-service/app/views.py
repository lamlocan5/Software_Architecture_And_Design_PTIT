import logging
from decimal import Decimal

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bill, BillItem
from .serializers import BillSerializer, CreateBillInternalSerializer

logger = logging.getLogger(__name__)


def verify_internal_key(request):
    """Kiểm tra header X-Internal-Key khớp với INTERNAL_SERVICE_KEY."""
    key = request.headers.get('X-Internal-Key', '')
    return key == settings.INTERNAL_SERVICE_KEY


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    """Danh sách và chi tiết hóa đơn + action thanh toán."""

    queryset = Bill.objects.all().order_by('-created_at')
    serializer_class = BillSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset

    @action(detail=True, methods=['put'], url_path='pay')
    def pay(self, request, pk=None):
        """
        PUT /api/v1/bills/{id}/pay/
        Chuyển trạng thái hóa đơn thành 'paid' và lưu thời điểm thanh toán.
        """
        bill = self.get_object()
        if bill.status == 'paid':
            return Response(
                {'error': 'Hóa đơn này đã được thanh toán.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if bill.status == 'cancelled':
            return Response(
                {'error': 'Không thể thanh toán hóa đơn đã hủy.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        bill.status = 'paid'
        bill.paid_at = timezone.now()
        bill.save(update_fields=['status', 'paid_at'])
        logger.info(f"Bill {bill.id} đã được thanh toán.")
        return Response(BillSerializer(bill).data)


class CreateBillInternalView(APIView):
    """
    POST /api/v1/internal/create-bill/
    Internal endpoint: chỉ gọi từ clinical-service, xác thực bằng X-Internal-Key.
    """

    def post(self, request):
        if not verify_internal_key(request):
            return Response(
                {'error': 'Unauthorized: Invalid internal service key.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CreateBillInternalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        bill = Bill.objects.create(
            patient_id=data['patient_id'],
            prescription_id=data.get('prescription_id'),
            status='draft',
        )

        for item_data in data['items']:
            BillItem.objects.create(
                bill=bill,
                description=item_data['description'],
                unit_price=Decimal(str(item_data.get('unit_price', 0))),
                quantity=int(item_data['quantity']),
            )

        bill.recalculate_total()
        logger.info(f"Bill {bill.id} đã được tạo cho patient {data['patient_id']} "
                    f"(prescription {data.get('prescription_id')}), total: {bill.total_amount}")
        return Response(BillSerializer(bill).data, status=status.HTTP_201_CREATED)
