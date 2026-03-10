"""Context processors for store app."""
from .cart import CartService


def cart_total(request):
    """Expose cart item count for navbar badge."""
    cart = CartService(request)
    return {'cart_item_count': cart.get_item_count()}
