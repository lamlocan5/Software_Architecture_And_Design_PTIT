from django.db import models


class Book(models.Model):
    """Read-only Book model for shared DB access"""
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()

    class Meta:
        db_table = 'books_book'
        managed = False  # Managed by book-service/monolith

class Cart(models.Model):
    """Cart model for cart-service"""
    customer_id = models.IntegerField()  # References customer from customer-service
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_cart'


class CartItem(models.Model):
    """Cart item model"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()  # logical reference
    # We can't easily use ForeignKey across apps without migrations complaining if not careful, 
    # but since we set managed=False, we can try to use it or just query it manually in serializer.
    # Manual query in serializer is safer for "microservice" separation emulation.
    quantity = models.IntegerField()
    
    class Meta:
        db_table = 'cart_cartitem'
        # unique_together = ['cart', 'book_id'] # Removed to match Monolith schema interpretation
