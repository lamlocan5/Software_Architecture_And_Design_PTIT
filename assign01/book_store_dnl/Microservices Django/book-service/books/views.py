from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Book
from .serializers import BookSerializer, UpdateStockSerializer


@api_view(['GET'])
def list_books(request):
    """List all books API endpoint"""
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    
    return Response({
        'success': True,
        'books': serializer.data,
        'count': books.count()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_book(request, book_id):
    """Get book by ID API endpoint"""
    try:
        book = Book.objects.get(id=book_id)
        serializer = BookSerializer(book)
        return Response({
            'success': True,
            'book': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Book.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Book not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
def update_stock(request, book_id):
    """Update book stock API endpoint"""
    try:
        book = Book.objects.get(id=book_id)
        serializer = UpdateStockSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        quantity = serializer.validated_data['quantity']
        operation = serializer.validated_data['operation']
        
        if operation == 'reduce':
            if book.stock < quantity:
                return Response({
                    'success': False,
                    'error': f'Insufficient stock. Available: {book.stock}'
                }, status=status.HTTP_400_BAD_REQUEST)
            book.stock -= quantity
        else:  # increase
            book.stock += quantity
        
        book.save()
        
        book_serializer = BookSerializer(book)
        return Response({
            'success': True,
            'message': 'Stock updated successfully',
            'book': book_serializer.data
        }, status=status.HTTP_200_OK)
    
    except Book.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Book not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def check_stock(request):
    """Check if books have sufficient stock (batch check)"""
    book_ids = request.data.get('book_ids', [])
    quantities = request.data.get('quantities', {})
    
    results = {}
    all_available = True
    
    for book_id in book_ids:
        try:
            book = Book.objects.get(id=book_id)
            required_quantity = quantities.get(str(book_id), 1)
            
            if book.stock >= required_quantity:
                results[book_id] = {
                    'available': True,
                    'stock': book.stock
                }
            else:
                results[book_id] = {
                    'available': False,
                    'stock': book.stock,
                    'required': required_quantity
                }
                all_available = False
        except Book.DoesNotExist:
            results[book_id] = {
                'available': False,
                'error': 'Book not found'
            }
            all_available = False
    
    return Response({
        'success': True,
        'all_available': all_available,
        'results': results
    }, status=status.HTTP_200_OK)
