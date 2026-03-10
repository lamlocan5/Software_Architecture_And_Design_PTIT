"""
Session-based Shopping Cart.
CartService: add(product, quantity), remove(product), get_total_price(), clear().
"""
from decimal import Decimal
from django.conf import settings
from .models import Book


class CartService:
    """Session-based cart. Key: 'cart' -> dict of {product_id: quantity}."""

    CART_SESSION_KEY = 'cart'

    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(self.CART_SESSION_KEY)
        if cart is None:
            cart = {}
        self._cart = cart

    def _save(self):
        self.session[self.CART_SESSION_KEY] = self._cart
        self.session.modified = True

    def add(self, product, quantity=1):
        """Add product (Book) with quantity. Merges if already in cart."""
        pid = str(product.pk)
        self._cart[pid] = self._cart.get(pid, 0) + quantity
        self._save()

    def remove(self, product):
        """Remove product from cart."""
        pid = str(product.pk)
        if pid in self._cart:
            del self._cart[pid]
            self._save()

    def set_quantity(self, product, quantity):
        """Set quantity for product. Remove if quantity <= 0."""
        pid = str(product.pk)
        if quantity <= 0:
            self.remove(product)
            return
        self._cart[pid] = quantity
        self._save()

    def get_quantity(self, product):
        """Get quantity for a product."""
        return self._cart.get(str(product.pk), 0)

    def get_total_price(self):
        """Sum of (price * quantity) for all items in cart."""
        total = Decimal('0')
        for pid, qty in self._cart.items():
            try:
                book = Book.objects.get(pk=pid)
                total += book.price * qty
            except Book.DoesNotExist:
                pass
        return total

    def get_item_count(self):
        """Total number of items (sum of quantities)."""
        return sum(self._cart.values())

    def clear(self):
        """Empty the cart."""
        self._cart = {}
        self._save()

    def __iter__(self):
        """Yield (book, quantity) for each cart item."""
        book_ids = list(self._cart.keys())
        books = Book.objects.filter(pk__in=book_ids)
        book_map = {str(b.pk): b for b in books}
        for pid in book_ids:
            book = book_map.get(pid)
            if book:
                yield book, self._cart[pid]

    def get_items(self):
        """List of (book, quantity) for template."""
        return list(self.__iter__())

    def get_items_with_subtotals(self):
        """List of (book, quantity, subtotal) for template."""
        return [(book, qty, book.price * qty) for book, qty in self.get_items()]
