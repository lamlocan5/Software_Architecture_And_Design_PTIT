import logging
import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Doctor
from .serializers import DoctorSerializer

logger = logging.getLogger(__name__)


class DoctorViewSet(viewsets.ModelViewSet):
    """CRUD bác sĩ + custom action lấy lịch hẹn từ clinical-service."""

    queryset = Doctor.objects.all().order_by('-created_at')
    serializer_class = DoctorSerializer

    @action(detail=True, methods=['get'], url_path='appointments')
    def appointments(self, request, pk=None):
        """
        GET /api/v1/doctors/{id}/appointments/
        Gọi sang clinical-service để lấy danh sách lịch hẹn của bác sĩ.
        """
        doctor = self.get_object()
        clinical_url = getattr(settings, 'CLINICAL_SERVICE_URL', 'http://clinical-service:8000')
        try:
            response = requests.get(
                f"{clinical_url}/api/v1/appointments/",
                params={'doctor_id': doctor.id},
                headers={'X-Internal-Key': settings.INTERNAL_SERVICE_KEY},
                timeout=5,
            )
            response.raise_for_status()
            return Response(response.json())
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout khi gọi clinical-service cho doctor {doctor.id}")
            return Response(
                {'error': 'clinical-service không phản hồi (timeout)'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Lỗi gọi clinical-service cho doctor {doctor.id}: {e}")
            return Response(
                {'error': 'Không thể kết nối tới clinical-service', 'detail': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
