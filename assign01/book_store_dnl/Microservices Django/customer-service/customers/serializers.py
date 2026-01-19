from rest_framework import serializers
from .models import Customer
from django.contrib.auth.hashers import make_password


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model"""
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email']


class RegisterSerializer(serializers.Serializer):
    """Serializer for customer registration"""
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    
    def validate_email(self, value):
        """Check if email already exists"""
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def create(self, validated_data):
        """Create customer with hashed password"""
        customer = Customer.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return customer


class LoginSerializer(serializers.Serializer):
    """Serializer for customer login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
