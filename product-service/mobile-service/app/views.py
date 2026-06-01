from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Mobile
from .serializers import MobileSerializer


@api_view(['GET', 'POST'])
def mobile_list(request):
    """
    GET  /mobiles/  — Danh sách tất cả mobile
    POST /mobiles/  — Tạo mobile mới (dùng bởi staff-service)
    """
    if request.method == 'GET':
        mobiles = Mobile.objects.all()
        serializer = MobileSerializer(mobiles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MobileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def mobile_detail(request, pk):
    """
    GET    /mobiles/<id>/  — Chi tiết mobile
    PUT    /mobiles/<id>/  — Cập nhật mobile
    DELETE /mobiles/<id>/  — Xóa mobile
    """
    try:
        mobile = Mobile.objects.get(pk=pk)
    except Mobile.DoesNotExist:
        return Response({'error': 'Mobile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MobileSerializer(mobile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MobileSerializer(mobile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        mobile.delete()
        return Response({'message': 'Mobile deleted'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def mobile_search(request):
    """
    GET /mobiles/search/?q=<query>  — Tìm kiếm mobile
    """
    query = request.query_params.get('q', '')
    if not query:
        mobiles = Mobile.objects.all()
    else:
        mobiles = Mobile.objects.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(cpu__icontains=query) |
            Q(os__icontains=query) |
            Q(description__icontains=query)
        )
    serializer = MobileSerializer(mobiles, many=True)
    return Response({
        'query': query,
        'count': mobiles.count(),
        'results': serializer.data
    })
