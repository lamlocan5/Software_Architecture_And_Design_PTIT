import logging

from django.conf import settings
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Medicine, StockTransaction
from .serializers import (
    DeductStockInternalSerializer,
    MedicineSerializer,
    StockTransactionSerializer,
    StockUpdateSerializer,
)

logger = logging.getLogger(__name__)


def verify_internal_key(request):
    key = request.headers.get('X-Internal-Key', '')
    return key == settings.INTERNAL_SERVICE_KEY


class MedicineViewSet(viewsets.ModelViewSet):
    """CRUD thuốc + custom action cập nhật tồn kho."""

    queryset = Medicine.objects.all().order_by('name')
    serializer_class = MedicineSerializer

    @action(detail=True, methods=['patch'], url_path='stock')
    def stock(self, request, pk=None):
        """
        PATCH /api/v1/medicines/{id}/stock/
        Nhập hoặc xuất kho thủ công.
        """
        medicine = self.get_object()
        serializer = StockUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        qty = data['quantity']
        tx_type = data['transaction_type']

        if tx_type == 'export' and medicine.stock < qty:
            return Response(
                {'error': f"Tồn kho không đủ. Hiện có: {medicine.stock}, yêu cầu: {qty}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tx_type == 'import':
            medicine.stock += qty
        else:
            medicine.stock -= qty
        medicine.save(update_fields=['stock', 'updated_at'])

        StockTransaction.objects.create(
            medicine=medicine,
            transaction_type=tx_type,
            quantity=qty,
            reference_id=data.get('reference_id', ''),
        )
        logger.info(f"Stock {tx_type}: {medicine.name} x{qty}, tồn còn: {medicine.stock}")
        return Response(MedicineSerializer(medicine).data)


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Danh sách lịch sử xuất nhập kho (read-only)."""

    queryset = StockTransaction.objects.all().order_by('-created_at')
    serializer_class = StockTransactionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        medicine_id = self.request.query_params.get('medicine_id')
        if medicine_id:
            queryset = queryset.filter(medicine_id=medicine_id)
        return queryset


class DeductStockInternalView(APIView):
    """
    POST /api/v1/internal/deduct-stock/
    Internal endpoint: chỉ gọi từ clinical-service, xác thực bằng X-Internal-Key.
    Trừ kho từng loại thuốc, ghi StockTransaction, trả về danh sách với unit_price.
    """

    def post(self, request):
        if not verify_internal_key(request):
            return Response(
                {'error': 'Unauthorized: Invalid internal service key.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = DeductStockInternalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        prescription_id = str(data['prescription_id'])
        items_data = data['items']

        # Validate tất cả trước khi thực hiện bất kỳ thao tác nào
        medicines = []
        for item in items_data:
            name = item['medicine_name']
            qty = int(item['quantity'])
            try:
                med = Medicine.objects.get(name=name)
            except Medicine.DoesNotExist:
                return Response(
                    {'error': f"Thuốc '{name}' không tồn tại trong kho."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if med.stock < qty:
                return Response(
                    {'error': f"Tồn kho '{name}' không đủ. Hiện có: {med.stock}, yêu cầu: {qty}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            medicines.append((med, qty))

        # Thực hiện trừ kho trong transaction
        result_items = []
        with transaction.atomic():
            for med, qty in medicines:
                med.stock -= qty
                med.save(update_fields=['stock', 'updated_at'])
                StockTransaction.objects.create(
                    medicine=med,
                    transaction_type='export',
                    quantity=qty,
                    reference_id=prescription_id,
                )
                result_items.append({
                    'medicine_name': med.name,
                    'quantity': qty,
                    'unit_price': str(med.unit_price),
                })
                logger.info(f"Deducted {qty}x {med.name} for prescription {prescription_id}")

        return Response({'success': True, 'items': result_items})
