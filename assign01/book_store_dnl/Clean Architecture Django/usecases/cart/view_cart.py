"""Use case: View cart contents"""
from typing import Protocol
from domain.entities.cart import Cart


class CartRepository(Protocol):
    """Repository interface for cart data access"""
    
    def get_or_create(self, customer_id: int) -> Cart:
        """Get or create cart for customer"""
        ...


class ViewCart:
    """Use case for viewing shopping cart"""
    
    def __init__(self, cart_repository: CartRepository):
        self.cart_repository = cart_repository
    
    def execute(self, customer_id: int) -> dict:
        """
        View cart contents with calculated totals
        
        Args:
            customer_id: Customer ID
        
        Returns:
            dict with cart items and total
        """
        cart = self.cart_repository.get_or_create(customer_id)
        
        # Calculate totals using domain logic
        total = cart.calculate_total()
        item_count = cart.get_item_count()
        
        return {
            'success': True,
            'cart': cart,
            'total': total,
            'item_count': item_count
        }
