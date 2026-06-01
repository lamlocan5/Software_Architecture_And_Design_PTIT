from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Laptop
from .serializers import LaptopSerializer


@api_view(['GET', 'POST'])
def laptop_list(request):
    """
    GET  /laptops/  — Danh sách tất cả laptop
    POST /laptops/  — Tạo laptop mới (dùng bởi staff-service)
    """
    if request.method == 'GET':
        laptops = Laptop.objects.all()
        serializer = LaptopSerializer(laptops, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = LaptopSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def laptop_detail(request, pk):
    """
    GET    /laptops/<id>/  — Chi tiết laptop
    PUT    /laptops/<id>/  — Cập nhật laptop
    DELETE /laptops/<id>/  — Xóa laptop
    """
    try:
        laptop = Laptop.objects.get(pk=pk)
    except Laptop.DoesNotExist:
        return Response({'error': 'Laptop not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LaptopSerializer(laptop)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = LaptopSerializer(laptop, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        laptop.delete()
        return Response({'message': 'Laptop deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def laptop_search(request):
    """
    GET /laptops/search/?q=<query>  — Tìm kiếm laptop
    """
    query = request.query_params.get('q', '')
    if not query:
        laptops = Laptop.objects.all()
    else:
        laptops = Laptop.objects.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(cpu__icontains=query) |
            Q(description__icontains=query)
        )
    serializer = LaptopSerializer(laptops, many=True)
    return Response({
        'query': query,
        'count': laptops.count(),
        'results': serializer.data
    })
