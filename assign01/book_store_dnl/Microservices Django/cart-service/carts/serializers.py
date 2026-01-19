from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model"""
    book_title = serializers.SerializerMethodField()
    book_price = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'book_id', 'book_title', 'book_price', 'quantity', 'subtotal']

    def get_book_title(self, obj):
        from .models import Book
        try:
            return Book.objects.get(id=obj.book_id).title
        except Book.DoesNotExist:
            return "Unknown Book"

    def get_book_price(self, obj):
        from .models import Book
        try:
            return Book.objects.get(id=obj.book_id).price
        except Book.DoesNotExist:
            return 0.0

    def get_subtotal(self, obj):
        price = self.get_book_price(obj)
        return price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model"""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'items', 'total', 'item_count', 'created_at']
    
    def get_total(self, obj):
        """Calculate cart total"""
        total = 0
        from .models import Book
        # Optimization: Fetch all books at once could be better but this is simple
        for item in obj.items.all():
            try:
                price = Book.objects.get(id=item.book_id).price
                total += price * item.quantity
            except Book.DoesNotExist:
                pass
        return total
    
    def get_item_count(self, obj):
        """Get number of items in cart"""
        return obj.items.count()


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding item to cart"""
    customer_id = serializers.IntegerField()
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
