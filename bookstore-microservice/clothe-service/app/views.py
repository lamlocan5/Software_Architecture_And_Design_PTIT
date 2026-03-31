from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Clothing, Category
from .serializers import ClothingSerializer, CategorySerializer


class ClothingListCreate(APIView):

    def get(self, request):
        clothes = Clothing.objects.select_related('category').all()
        serializer = ClothingSerializer(clothes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClothingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClothingDetail(APIView):

    def get_object(self, pk):
        try:
            return Clothing.objects.get(pk=pk)
        except Clothing.DoesNotExist:
            return None

    def get(self, request, pk):
        clothing = self.get_object(pk)
        if not clothing:
            return Response({'error': 'Không tìm thấy sản phẩm'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClothingSerializer(clothing).data)

    def put(self, request, pk):
        clothing = self.get_object(pk)
        if not clothing:
            return Response({'error': 'Không tìm thấy sản phẩm'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClothingSerializer(clothing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        clothing = self.get_object(pk)
        if not clothing:
            return Response({'error': 'Không tìm thấy sản phẩm'}, status=status.HTTP_404_NOT_FOUND)
        clothing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreate(APIView):

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại quần áo'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CategorySerializer(category).data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại quần áo'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại quần áo'}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

