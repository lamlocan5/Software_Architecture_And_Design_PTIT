from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Electronic, ElectronicCategory
from .serializers import ElectronicSerializer, ElectronicCategorySerializer


class ElectronicListCreate(APIView):

    def get(self, request):
        electronics = Electronic.objects.select_related('category').all()
        serializer = ElectronicSerializer(electronics, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ElectronicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ElectronicDetail(APIView):

    def get_object(self, pk):
        try:
            return Electronic.objects.get(pk=pk)
        except Electronic.DoesNotExist:
            return None

    def get(self, request, pk):
        electronic = self.get_object(pk)
        if not electronic:
            return Response({'error': 'Không tìm thấy sản phẩm điện tử'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ElectronicSerializer(electronic).data)

    def put(self, request, pk):
        electronic = self.get_object(pk)
        if not electronic:
            return Response({'error': 'Không tìm thấy sản phẩm điện tử'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ElectronicSerializer(electronic, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        electronic = self.get_object(pk)
        if not electronic:
            return Response({'error': 'Không tìm thấy sản phẩm điện tử'}, status=status.HTTP_404_NOT_FOUND)
        electronic.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ElectronicCategoryListCreate(APIView):

    def get(self, request):
        categories = ElectronicCategory.objects.all()
        serializer = ElectronicCategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ElectronicCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ElectronicCategoryDetail(APIView):

    def get_object(self, pk):
        try:
            return ElectronicCategory.objects.get(pk=pk)
        except ElectronicCategory.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại điện tử'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ElectronicCategorySerializer(category).data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại điện tử'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ElectronicCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại điện tử'}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

