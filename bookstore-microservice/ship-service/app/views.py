from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentList(APIView):
    def get(self, request):
        shipments = Shipment.objects.all().order_by('-created_at')
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)


class ShipmentCreate(APIView):
    def post(self, request):
        for f in ['order_id', 'customer_id']:
            if request.data.get(f) in [None, '']:
                return Response({"error": f"{f} là bắt buộc"}, status=status.HTTP_400_BAD_REQUEST)

        shipment = Shipment.objects.create(
            order_id=request.data.get('order_id'),
            customer_id=request.data.get('customer_id'),
            receiver_name=request.data.get('receiver_name', '') or '',
            phone=request.data.get('phone', '') or '',
            address=request.data.get('address', '') or '',
            carrier=request.data.get('carrier', '') or '',
            tracking_number=request.data.get('tracking_number', '') or '',
            status='pending',
        )
        return Response(ShipmentSerializer(shipment).data, status=status.HTTP_201_CREATED)


class ShipmentDetail(APIView):
    def get(self, request, shipment_id):
        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return Response({"error": "Không tìm thấy shipment"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ShipmentSerializer(shipment).data)


class ShipmentStatusUpdate(APIView):
    VALID_STATUSES = ['pending', 'picked', 'shipping', 'delivered', 'failed', 'cancelled']

    def patch(self, request, shipment_id):
        try:
            shipment = Shipment.objects.get(id=shipment_id)
        except Shipment.DoesNotExist:
            return Response({"error": "Không tìm thấy shipment"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in self.VALID_STATUSES:
            return Response(
                {"error": f"Trạng thái không hợp lệ. Chọn: {self.VALID_STATUSES}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        shipment.status = new_status
        shipment.save()
        return Response(ShipmentSerializer(shipment).data)


class OrderShipments(APIView):
    def get(self, request, order_id):
        shipments = Shipment.objects.filter(order_id=order_id).order_by('-created_at')
        return Response(ShipmentSerializer(shipments, many=True).data)


class CustomerShipments(APIView):
    def get(self, request, customer_id):
        shipments = Shipment.objects.filter(customer_id=customer_id).order_by('-created_at')
        return Response(ShipmentSerializer(shipments, many=True).data)

