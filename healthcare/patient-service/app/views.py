import logging

import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Patient
from .serializers import PatientSerializer

logger = logging.getLogger(__name__)


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD bệnh nhân + custom action lấy lịch hẹn từ clinical-service."""

    queryset = Patient.objects.all().order_by('-created_at')
    serializer_class = PatientSerializer

    @action(detail=True, methods=['get'], url_path='appointments')
    def appointments(self, request, pk=None):
        """
        GET /api/v1/patients/{id}/appointments/
        Gọi sang clinical-service để lấy danh sách lịch hẹn của bệnh nhân.
        """
        patient = self.get_object()
        clinical_url = getattr(settings, 'CLINICAL_SERVICE_URL', 'http://clinical-service:8000')
        try:
            response = requests.get(
                f"{clinical_url}/api/v1/appointments/",
                params={'patient_id': patient.id},
                headers={'X-Internal-Key': settings.INTERNAL_SERVICE_KEY},
                timeout=5,
            )
            response.raise_for_status()
            return Response(response.json())
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout khi gọi clinical-service cho patient {patient.id}")
            return Response(
                {'error': 'clinical-service không phản hồi (timeout)'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Lỗi gọi clinical-service cho patient {patient.id}: {e}")
            return Response(
                {'error': 'Không thể kết nối tới clinical-service', 'detail': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
