from django.db import models
from django.contrib.auth.models import User
from catalog.models import Book

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def compute_total(self):
        total = 0
        for item in self.items.all():
            total += item.price * item.quantity
        self.total_price = total
        self.save()
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def update_quantity(self, qty):
        self.quantity = qty
        self.save()
