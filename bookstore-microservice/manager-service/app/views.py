from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Manager
from .serializers import ManagerSerializer


class ManagerListCreate(APIView):
    def get(self, request):
        managers = Manager.objects.all().order_by("-created_at")
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            manager = serializer.save()
            return Response(ManagerSerializer(manager).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagerDetail(APIView):
    def get_object(self, pk):
        try:
            return Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            return None

    def patch(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        fields_to_update = []

        if "active" in request.data:
            manager.active = bool(request.data.get("active"))
            fields_to_update.append("active")

        if "name" in request.data:
            manager.name = str(request.data.get("name") or "").strip()
            fields_to_update.append("name")

        if "email" in request.data:
            manager.email = str(request.data.get("email") or "").strip().lower()
            fields_to_update.append("email")

        if not fields_to_update:
            return Response({"detail": "No fields to update"}, status=status.HTTP_400_BAD_REQUEST)

        manager.save(update_fields=list(dict.fromkeys(fields_to_update)))
        return Response(ManagerSerializer(manager).data)

    def delete(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        manager.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

