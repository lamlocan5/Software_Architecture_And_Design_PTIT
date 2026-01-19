"""Use case: Remove item from cart"""
from typing import Protocol
from domain.entities.cart import Cart


class CartRepository(Protocol):
    """Repository interface for cart data access"""
    
    def get_or_create(self, customer_id: int) -> Cart:
        """Get or create cart for customer"""
        ...
    
    def save(self, cart: Cart) -> Cart:
        """Save cart"""
        ...


class RemoveFromCart:
    """Use case for removing item from shopping cart"""
    
    def __init__(self, cart_repository: CartRepository):
        self.cart_repository = cart_repository
    
    def execute(self, customer_id: int, book_id: int) -> dict:
        """
        Remove item from cart
        
        Args:
            customer_id: Customer ID
            book_id: Book ID to remove
        
        Returns:
            dict with success status and message
        """
        try:
            # Get cart
            cart = self.cart_repository.get_or_create(customer_id)
            
            # Remove item (domain logic)
            cart.remove_item(book_id)
            
            # Save cart
            self.cart_repository.save(cart)
            
            return {
                'success': True,
                'message': 'Item removed from cart',
                'cart': cart
            }
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
