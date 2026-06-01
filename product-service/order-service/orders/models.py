from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('cancelled', 'Đã hủy'),
    ]

    customer_id = models.IntegerField()
    customer_name = models.CharField(max_length=200)
    customer_email = models.CharField(max_length=200, blank=True)
    shipping_address = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} — {self.customer_name} ({self.status})"

    def recalculate_total(self):
        self.total_price = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=['total_price'])


class OrderItem(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES)
    product_name = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField(default=1)

    class Meta:
        db_table = 'order_items'

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order #{self.order_id})"
