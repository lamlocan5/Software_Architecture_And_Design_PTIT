from rest_framework import serializers
from .models import Customer, Cart, CartItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'created_at']


class CustomerRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    full_name = serializers.CharField(max_length=200, required=False, default='')
    phone = serializers.CharField(max_length=20, required=False, default='')


class CustomerLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_type', 'product_name', 'price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    customer_username = serializers.CharField(source='customer.username', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'customer_username', 'items', 'total_price', 'created_at', 'updated_at']

    def get_total_price(self, obj):
        return obj.total_price
