import logging

import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Appointment, Prescription
from .serializers import AppointmentSerializer, PrescriptionSerializer

logger = logging.getLogger(__name__)


class AppointmentViewSet(viewsets.ModelViewSet):
    """Quản lý lịch hẹn. Hỗ trợ filter theo patient_id."""

    serializer_class = AppointmentSerializer
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        queryset = Appointment.objects.all().order_by('-created_at')
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


class PrescriptionViewSet(viewsets.ModelViewSet):
    """
    Tạo đơn thuốc và tự động:
    1. Trừ kho tại inventory-service
    2. Tạo hóa đơn nháp tại billing-service
    """

    queryset = Prescription.objects.all().order_by('-created_at')
    serializer_class = PrescriptionSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def _get_patient_info(self, patient_id):
        """Lấy thông tin bệnh nhân từ patient-service, cache 60s."""
        cache_key = f"patient_info_{patient_id}"
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit: patient_{patient_id}")
            return cached
        patient_url = getattr(settings, 'PATIENT_SERVICE_URL', 'http://patient-service:8000')
        try:
            resp = requests.get(
                f"{patient_url}/api/v1/patients/{patient_id}/",
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                cache.set(cache_key, data, 60)
                return data
        except requests.exceptions.RequestException as e:
            logger.warning(f"Không thể lấy thông tin patient {patient_id}: {e}")
        return None

    def _notify_inventory(self, prescription):
        """Gọi inventory-service để trừ kho. Trả về items với unit_price nếu thành công."""
        inventory_url = getattr(settings, 'INVENTORY_SERVICE_URL', 'http://inventory-service:8000')
        items = [
            {'medicine_name': item.medicine_name, 'quantity': item.quantity}
            for item in prescription.items.all()
        ]
        payload = {'prescription_id': prescription.id, 'items': items}
        try:
            resp = requests.post(
                f"{inventory_url}/api/v1/internal/deduct-stock/",
                json=payload,
                headers={'X-Internal-Key': settings.INTERNAL_SERVICE_KEY},
                timeout=10,
            )
            if resp.status_code == 200:
                logger.info(f"Inventory deducted for prescription {prescription.id}")
                return resp.json().get('items', [])
            else:
                logger.warning(
                    f"inventory-service trả {resp.status_code} cho prescription {prescription.id}: {resp.text}"
                )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Lỗi gọi inventory-service cho prescription {prescription.id}: {e}")
        return []

    def _notify_billing(self, prescription, inventory_items):
        """Gọi billing-service tạo hóa đơn nháp với giá từ inventory."""
        billing_url = getattr(settings, 'BILLING_SERVICE_URL', 'http://billing-service:8000')
        # Tạo map medicine_name → unit_price từ inventory response
        price_map = {i['medicine_name']: i.get('unit_price', 0) for i in inventory_items}

        items = [
            {
                'description': item.medicine_name,
                'unit_price': str(price_map.get(item.medicine_name, 0)),
                'quantity': item.quantity,
            }
            for item in prescription.items.all()
        ]
        payload = {
            'patient_id': prescription.patient_id,
            'prescription_id': prescription.id,
            'items': items,
        }
        try:
            resp = requests.post(
                f"{billing_url}/api/v1/internal/create-bill/",
                json=payload,
                headers={'X-Internal-Key': settings.INTERNAL_SERVICE_KEY},
                timeout=10,
            )
            if resp.status_code in [200, 201]:
                logger.info(f"Bill created for prescription {prescription.id}")
            else:
                logger.warning(
                    f"billing-service trả {resp.status_code} cho prescription {prescription.id}: {resp.text}"
                )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Lỗi gọi billing-service cho prescription {prescription.id}: {e}")

    def _notify_services(self, prescription):
        """Best-effort: gọi cả 2 services, không rollback nếu lỗi."""
        inventory_items = self._notify_inventory(prescription)
        self._notify_billing(prescription, inventory_items)

    def perform_create(self, serializer):
        prescription = serializer.save()
        self._notify_services(prescription)
