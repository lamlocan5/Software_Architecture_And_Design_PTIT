from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddToCartSerializer
from .services import CustomerServiceClient, BookServiceClient


# Initialize service clients
customer_client = CustomerServiceClient()
book_client = BookServiceClient()


@api_view(['POST'])
def add_to_cart(request):
    """Add item to cart API endpoint"""
    serializer = AddToCartSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    customer_id = serializer.validated_data['customer_id']
    book_id = serializer.validated_data['book_id']
    quantity = serializer.validated_data['quantity']
    
    # Verify customer exists (inter-service call)
    if not customer_client.verify_customer(customer_id):
        return Response({
            'success': False,
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get book details (inter-service call)
    book = book_client.get_book(book_id)
    if not book:
        return Response({
            'success': False,
            'error': 'Book not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check stock (inter-service call)
    if not book_client.check_stock(book_id, quantity):
        return Response({
            'success': False,
            'error': f"Insufficient stock. Available: {book.get('stock', 0)}"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create cart
    cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
    
    # Check if item already exists in cart
    try:
        cart_item = CartItem.objects.get(cart=cart, book_id=book_id)
        cart_item.quantity += quantity
        cart_item.save()
        message = f'Updated quantity of "{book["title"]}" in cart'
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            cart=cart,
            book_id=book_id,
            book_title=book['title'],
            book_price=book['price'],
            quantity=quantity
        )
        message = f'Added "{book["title"]}" to cart'
    
    cart_serializer = CartSerializer(cart)
    return Response({
        'success': True,
        'message': message,
        'cart': cart_serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def view_cart(request, customer_id):
    """View cart API endpoint"""
    # Verify customer exists (inter-service call)
    if not customer_client.verify_customer(customer_id):
        return Response({
            'success': False,
            'error': 'Customer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response({
            'success': True,
            'cart': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Cart.DoesNotExist:
        # Return empty cart
        return Response({
            'success': True,
            'cart': {
                'customer_id': customer_id,
                'items': [],
                'total': 0,
                'item_count': 0
            }
        }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def remove_from_cart(request, item_id):
    """Remove item from cart API endpoint"""
    try:
        cart_item = CartItem.objects.get(id=item_id)
        book_title = cart_item.book_title
        cart_item.delete()
        
        return Response({
            'success': True,
            'message': f'Removed "{book_title}" from cart'
        }, status=status.HTTP_200_OK)
    
    except CartItem.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cart item not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def clear_cart(request, customer_id):
    """Clear entire cart API endpoint"""
    try:
        cart = Cart.objects.get(customer_id=customer_id)
        cart.items.all().delete()
        
        return Response({
            'success': True,
            'message': 'Cart cleared successfully'
        }, status=status.HTTP_200_OK)
    
    except Cart.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cart not found'
        }, status=status.HTTP_404_NOT_FOUND)
