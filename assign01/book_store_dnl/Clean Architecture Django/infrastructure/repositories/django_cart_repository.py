"""Django ORM implementation of CartRepository"""
from interfaces.repositories import CartRepository
from domain.entities.cart import Cart, CartItem
from infrastructure.database.models import CartModel, CartItemModel


class DjangoCartRepository(CartRepository):
    """Cart repository using Django ORM"""
    
    def get_or_create(self, customer_id: int) -> Cart:
        """Get or create cart for customer"""
        cart_model, created = CartModel.objects.get_or_create(
            customer_id=customer_id
        )
        
        return self._to_entity(cart_model)
    
    def save(self, cart: Cart) -> Cart:
        """Save cart and its items"""
        # Get or create cart model
        cart_model, _ = CartModel.objects.get_or_create(
            customer_id=cart.customer_id
        )
        
        # Delete existing items
        CartItemModel.objects.filter(cart=cart_model).delete()
        
        # Create new items
        for item in cart.items:
            CartItemModel.objects.create(
                cart=cart_model,
                book_id=item.book_id,
                quantity=item.quantity
            )
        
        return self._to_entity(cart_model)
    
    def delete_item(self, customer_id: int, book_id: int) -> None:
        """Delete specific item from cart"""
        try:
            cart_model = CartModel.objects.get(customer_id=customer_id)
            CartItemModel.objects.filter(cart=cart_model, book_id=book_id).delete()
        except CartModel.DoesNotExist:
            pass
    
    def _to_entity(self, model: CartModel) -> Cart:
        """Convert Django model to domain entity"""
        # Get cart items with related book data
        item_models = CartItemModel.objects.filter(cart=model).select_related('book')
        items = [
            CartItem(
                id=item_model.id,
                book_id=item_model.book_id,
                book_title=item_model.book.title,
                book_price=item_model.book.price,
                quantity=item_model.quantity
            )
            for item_model in item_models
        ]
        
        return Cart(
            id=model.id,
            customer_id=model.customer_id,
            items=items,
            created_at=model.created_at
        )
