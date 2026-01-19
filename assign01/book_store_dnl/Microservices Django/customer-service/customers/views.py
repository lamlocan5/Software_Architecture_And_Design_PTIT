from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password

from .models import Customer
from .serializers import CustomerSerializer, RegisterSerializer, LoginSerializer


@api_view(['POST'])
def register(request):
    """Register new customer API endpoint"""
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        customer = serializer.save()
        customer_serializer = CustomerSerializer(customer)
        return Response({
            'success': True,
            'message': 'Registration successful',
            'customer': customer_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'error': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    """Customer login API endpoint"""
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    
    try:
        customer = Customer.objects.get(email=email)
        
        if customer.password == password:
            customer_serializer = CustomerSerializer(customer)
            return Response({
                'success': True,
                'message': 'Login successful',
                'customer': customer_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    except Customer.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Invalid email or password'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def get_customer(request, customer_id):
    """Get customer by ID API endpoint"""
    try:
        customer = Customer.objects.get(id=customer_id)
        serializer = CustomerSerializer(customer)
        return Response({
            'success': True,
            'customer': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Customer.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
