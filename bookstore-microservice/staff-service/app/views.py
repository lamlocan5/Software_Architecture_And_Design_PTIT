from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Staff
from .serializers import StaffSerializer


class StaffListCreate(APIView):
    def get(self, request):
        staff = Staff.objects.all().order_by("-created_at")
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            staff = serializer.save()
            return Response(StaffSerializer(staff).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffDetail(APIView):
    def get_object(self, pk):
        try:
            return Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return None

    def patch(self, request, pk):
        staff = self.get_object(pk)
        if not staff:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        fields_to_update = []

        if "active" in request.data:
            staff.active = bool(request.data.get("active"))
            fields_to_update.append("active")

        if "name" in request.data:
            staff.name = str(request.data.get("name") or "").strip()
            fields_to_update.append("name")

        if "email" in request.data:
            staff.email = str(request.data.get("email") or "").strip().lower()
            fields_to_update.append("email")

        if not fields_to_update:
            return Response({"detail": "No fields to update"}, status=status.HTTP_400_BAD_REQUEST)

        staff.save(update_fields=list(dict.fromkeys(fields_to_update)))
        return Response(StaffSerializer(staff).data)

    def delete(self, request, pk):
        staff = self.get_object(pk)
        if not staff:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

