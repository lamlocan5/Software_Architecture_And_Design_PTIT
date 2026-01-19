"""Use case: Add item to cart"""
from typing import Protocol
from domain.entities.cart import Cart
from domain.entities.book import Book


class CartRepository(Protocol):
    """Repository interface for cart data access"""
    
    def get_or_create(self, customer_id: int) -> Cart:
        """Get or create cart for customer"""
        ...
    
    def save(self, cart: Cart) -> Cart:
        """Save cart"""
        ...


class BookRepository(Protocol):
    """Repository interface for book data access"""
    
    def find_by_id(self, book_id: int) -> Book | None:
        """Find book by ID"""
        ...
    
    def update(self, book: Book) -> Book:
        """Update book"""
        ...


class AddToCart:
    """Use case for adding item to shopping cart"""
    
    def __init__(self, cart_repository: CartRepository, book_repository: BookRepository):
        self.cart_repository = cart_repository
        self.book_repository = book_repository
    
    def execute(self, customer_id: int, book_id: int, quantity: int) -> dict:
        """
        Add item to cart
        
        Args:
            customer_id: Customer ID
            book_id: Book ID
            quantity: Quantity to add
        
        Returns:
            dict with success status and message or error
        """
        # Business rule: Quantity must be positive
        if quantity <= 0:
            return {
                'success': False,
                'error': 'Quantity must be positive'
            }
        
        # Find book
        book = self.book_repository.find_by_id(book_id)
        if not book:
            return {
                'success': False,
                'error': 'Book not found'
            }
        
        # Business rule: Check stock availability
        if not book.is_in_stock(quantity):
            return {
                'success': False,
                'error': f'Insufficient stock. Available: {book.stock}'
            }
        
        try:
            # Get or create cart
            cart = self.cart_repository.get_or_create(customer_id)
            
            # Add item to cart (domain logic handles duplicates)
            cart.add_item(
                book_id=book.id,
                book_title=book.title,
                book_price=book.price,
                quantity=quantity
            )
            
            # Save cart
            self.cart_repository.save(cart)
            
            return {
                'success': True,
                'message': f'Added "{book.title}" to cart',
                'cart': cart
            }
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
