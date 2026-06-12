from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Publisher, Category
from .serializers import BookSerializer, PublisherSerializer, ClothingSerializer, CategorySerializer, ElectronicSerializer

# Helper to get object
def get_product(pk, product_type):
    try:
        return Product.objects.get(pk=pk, product_type=product_type)
    except Product.DoesNotExist:
        return None

# ── Unified general endpoint for Cart/other services to get details by generic ID ──
class ProductDetailGeneric(APIView):
    def get(self, request, pk):
        try:
            prod = Product.objects.get(pk=pk)
            if prod.product_type == 'book':
                return Response(BookSerializer(prod).data)
            elif prod.product_type == 'clothing':
                return Response(ClothingSerializer(prod).data)
            elif prod.product_type == 'electronic':
                return Response(ElectronicSerializer(prod).data)
            return Response({'error': 'Unknown type'}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

# ── Books ─────────────────────────────────────────────────────────────────
class BookListCreate(APIView):
    def get(self, request):
        books = Product.objects.filter(product_type='book')
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookDetail(APIView):
    def get(self, request, pk):
        prod = get_product(pk, 'book')
        if not prod:
            return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookSerializer(prod).data)

    def put(self, request, pk):
        prod = get_product(pk, 'book')
        if not prod:
            return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(prod, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        prod = get_product(pk, 'book')
        if not prod:
            return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(prod, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        prod = get_product(pk, 'book')
        if not prod:
            return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
        prod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ── Publishers ────────────────────────────────────────────────────────────
class PublisherListCreate(APIView):
    def get(self, request):
        publishers = Publisher.objects.all()
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PublisherDetail(APIView):
    def get_object(self, pk):
        try:
            return Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            return None

    def get(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return Response({'error': 'Không tìm thấy nhà xuất bản'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PublisherSerializer(publisher).data)

    def put(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return Response({'error': 'Không tìm thấy nhà xuất bản'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PublisherSerializer(publisher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return Response({'error': 'Không tìm thấy nhà xuất bản'}, status=status.HTTP_404_NOT_FOUND)
        publisher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ── Clothes ────────────────────────────────────────────────────────────────
class ClothingListCreate(APIView):
    def get(self, request):
        clothes = Product.objects.filter(product_type='clothing')
        serializer = ClothingSerializer(clothes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClothingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClothingDetail(APIView):
    def get(self, request, pk):
        prod = get_product(pk, 'clothing')
        if not prod:
            return Response({'error': 'Không tìm thấy quần áo'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClothingSerializer(prod).data)

    def put(self, request, pk):
        prod = get_product(pk, 'clothing')
        if not prod:
            return Response({'error': 'Không tìm thấy quần áo'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClothingSerializer(prod, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        prod = get_product(pk, 'clothing')
        if not prod:
            return Response({'error': 'Không tìm thấy quần áo'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClothingSerializer(prod, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        prod = get_product(pk, 'clothing')
        if not prod:
            return Response({'error': 'Không tìm thấy quần áo'}, status=status.HTTP_404_NOT_FOUND)
        prod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ── Clothing Categories ────────────────────────────────────────────────────
class CategoryListCreate(APIView):
    def get(self, request):
        categories = Category.objects.filter(category_type='clothing')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['category_type'] = 'clothing'
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk, category_type='clothing')
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
        data = request.data.copy()
        data['category_type'] = 'clothing'
        serializer = CategorySerializer(category, data=data)
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

# ── Electronics ────────────────────────────────────────────────────────────
class ElectronicListCreate(APIView):
    def get(self, request):
        electronics = Product.objects.filter(product_type='electronic')
        serializer = ElectronicSerializer(electronics, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ElectronicSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ElectronicDetail(APIView):
    def get(self, request, pk):
        prod = get_product(pk, 'electronic')
        if not prod:
            return Response({'error': 'Không tìm thấy sản phẩm điện tử'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ElectronicSerializer(prod).data)

    def put(self, request, pk):
        prod = get_product(pk, 'electronic')
        if not prod:
            return Response({'error': 'Không tìm thấy sản phẩm điện tử'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ElectronicSerializer(prod, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        prod = get_product(pk, 'electronic')
        if not prod:
            return Response({'error': 'Không tìm thấy sản phẩm điện tử'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ElectronicSerializer(prod, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        prod = get_product(pk, 'electronic')
        if not prod:
            return Response({'error': 'Không tìm thấy sản phẩm điện tử'}, status=status.HTTP_404_NOT_FOUND)
        prod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ── Electronic Categories ──────────────────────────────────────────────────
class ElectronicCategoryListCreate(APIView):
    def get(self, request):
        categories = Category.objects.filter(category_type='electronic')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['category_type'] = 'electronic'
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ElectronicCategoryDetail(APIView):
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk, category_type='electronic')
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại đồ điện tử'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CategorySerializer(category).data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại đồ điện tử'}, status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['category_type'] = 'electronic'
        serializer = CategorySerializer(category, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({'error': 'Không tìm thấy loại đồ điện tử'}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
