import uuid
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Staff
from .serializers import StaffSerializer, StaffLoginSerializer, StaffRegisterSerializer

# Simple in-memory token store (production should use Redis or DB)
_active_tokens = {}


@api_view(['POST'])
def staff_register(request):
    """
    POST /staff/register/  — Tạo tài khoản staff mới
    """
    serializer = StaffRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    if Staff.objects.filter(username=data['username']).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    if Staff.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

    staff = Staff(username=data['username'], email=data['email'], role=data['role'])
    staff.set_password(data['password'])
    staff.save()

    return Response({
        'message': 'Staff registered successfully',
        'staff': StaffSerializer(staff).data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def staff_login(request):
    """
    POST /staff/login/  — Đăng nhập staff, trả về token
    """
    serializer = StaffLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        staff = Staff.objects.get(username=data['username'])
    except Staff.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if not staff.check_password(data['password']):
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    token = str(uuid.uuid4())
    _active_tokens[token] = staff.id
    return Response({
        'token': token,
        'staff': StaffSerializer(staff).data
    })


@api_view(['GET'])
def staff_profile(request):
    """
    GET /staff/profile/?token=<token>  — Lấy thông tin staff từ token
    """
    token = request.query_params.get('token')
    if not token or token not in _active_tokens:
        return Response({'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
    staff_id = _active_tokens[token]
    try:
        staff = Staff.objects.get(id=staff_id)
        return Response(StaffSerializer(staff).data)
    except Staff.DoesNotExist:
        return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_item(request):
    """
    POST /staff/items/add/  — Nhập item mới (laptop hoặc mobile)
    Body: { "type": "laptop"|"mobile", "token": "...", ...item_fields }
    """
    token = request.data.get('token')
    if not token or token not in _active_tokens:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    item_type = request.data.get('type')
    if item_type not in ['laptop', 'mobile']:
        return Response({'error': 'type must be "laptop" or "mobile"'}, status=status.HTTP_400_BAD_REQUEST)

    # Build payload (exclude 'type' and 'token')
    payload = {k: v for k, v in request.data.items() if k not in ['type', 'token']}

    try:
        if item_type == 'laptop':
            url = f"{settings.LAPTOP_SERVICE_URL}/laptops/"
        else:
            url = f"{settings.MOBILE_SERVICE_URL}/mobiles/"

        resp = requests.post(url, json=payload, timeout=10)
        return Response(resp.json(), status=resp.status_code)
    except requests.RequestException as e:
        return Response({'error': f'Service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['PUT'])
def update_item(request, item_type, pk):
    """
    PUT /staff/items/<laptop|mobile>/<id>/update/  — Cập nhật item
    Body: { "token": "...", ...update_fields }
    """
    token = request.data.get('token')
    if not token or token not in _active_tokens:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    if item_type not in ['laptop', 'mobile']:
        return Response({'error': 'item_type must be "laptop" or "mobile"'}, status=status.HTTP_400_BAD_REQUEST)

    payload = {k: v for k, v in request.data.items() if k != 'token'}

    try:
        if item_type == 'laptop':
            url = f"{settings.LAPTOP_SERVICE_URL}/laptops/{pk}/"
        else:
            url = f"{settings.MOBILE_SERVICE_URL}/mobiles/{pk}/"

        resp = requests.put(url, json=payload, timeout=10)
        return Response(resp.json(), status=resp.status_code)
    except requests.RequestException as e:
        return Response({'error': f'Service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
def list_items(request, item_type):
    """
    GET /staff/items/<laptop|mobile>/  — Xem danh sách sản phẩm
    """
    try:
        if item_type == 'laptop':
            url = f"{settings.LAPTOP_SERVICE_URL}/laptops/"
        elif item_type == 'mobile':
            url = f"{settings.MOBILE_SERVICE_URL}/mobiles/"
        else:
            return Response({'error': 'item_type must be "laptop" or "mobile"'}, status=status.HTTP_400_BAD_REQUEST)

        resp = requests.get(url, timeout=10)
        return Response(resp.json(), status=resp.status_code)
    except requests.RequestException as e:
        return Response({'error': f'Service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
