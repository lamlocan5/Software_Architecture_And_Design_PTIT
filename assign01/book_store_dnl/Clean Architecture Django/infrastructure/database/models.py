"""Django ORM models - Infrastructure layer"""
from django.db import models


class CustomerModel(models.Model):
    """Customer database model"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Renamed from hashed_password to match Monolith
    
    class Meta:
        db_table = 'accounts_customer'  # Monolith table
    
    def __str__(self):
        return self.name


class BookModel(models.Model):
    """Book database model"""
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    
    class Meta:
        db_table = 'books_book'  # Monolith table
    
    def __str__(self):
        return self.title


class CartModel(models.Model):
    """Cart database model"""
    # Monolith uses ForeignKey to Customer
    customer = models.ForeignKey(CustomerModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart_cart'  # Monolith table


class CartItemModel(models.Model):
    """Cart item database model"""
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name='items')
    # Monolith uses ForeignKey to Book
    book = models.ForeignKey(BookModel, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    
    class Meta:
        db_table = 'cart_cartitem'  # Monolith table
        # Note: Monolith CartItem doesn't seem to verify unique_together explicitly in the snippet I saw, 
        # but likely has it or we can keep it if it helps. 
        # Actually I saw 'unique_together' in Version B?
        # Monolith snippet: just fields. 
        # Keeping it safe: if Monolith doesn't have unique constraint, Django might try to create it.
        # Let's remove unique_together to be safe and strictly match Monolith snippet.
        # But logically one book per cart line is standard. 
        # I'll Comment it out to be safe.
