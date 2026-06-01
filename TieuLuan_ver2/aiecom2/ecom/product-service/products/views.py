"""
product-service/products/views.py
Endpoints:
  GET  /api/products/             → Danh sách sản phẩm (có filter)
  GET  /api/products/<id>/        → Chi tiết 1 sản phẩm
  GET  /api/products/by-ids/      → Lấy nhiều sản phẩm theo IDs (gọi bởi recommend-service)
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Product
from .serializers import ProductSerializer


class ProductListView(APIView):
    """GET /api/products/?search=...&category=..."""
    def get(self, request):
        products = Product.objects.all()
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')

        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        if category:
            products = products.filter(category=category)

        return Response({
            'count': products.count(),
            'products': ProductSerializer(products, many=True).data
        })


class ProductDetailView(APIView):
    """GET /api/products/<id>/"""
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            return Response(ProductSerializer(product).data)
        except Product.DoesNotExist:
            return Response({'error': 'Không tìm thấy sản phẩm'}, status=404)


class ProductsByIdsView(APIView):
    """
    GET /api/products/by-ids/?ids=1,2,3,4,5
    Được gọi bởi recommend-service và chat-service để lấy thông tin sản phẩm.
    """
    def get(self, request):
        ids_param = request.query_params.get('ids', '')
        if not ids_param:
            return Response({'products': []})

        try:
            ids = [int(i.strip()) for i in ids_param.split(',') if i.strip()]
        except ValueError:
            return Response({'error': 'ids phải là số'}, status=400)

        products = Product.objects.filter(id__in=ids)
        # Giữ đúng thứ tự theo ids truyền vào
        id_order = {pid: i for i, pid in enumerate(ids)}
        products = sorted(products, key=lambda p: id_order.get(p.id, 999))
        return Response({'products': ProductSerializer(products, many=True).data})
