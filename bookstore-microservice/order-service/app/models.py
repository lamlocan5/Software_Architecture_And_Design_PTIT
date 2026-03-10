from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping',  'Đang giao'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã huỷ'),
    ]

    customer_id  = models.IntegerField()
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - Customer {self.customer_id}"


class OrderItem(models.Model):
    order          = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book_id        = models.IntegerField()
    quantity       = models.IntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"OrderItem: Book {self.book_id} x{self.quantity}"
