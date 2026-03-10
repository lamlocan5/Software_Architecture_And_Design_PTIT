from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ lấy hàng'),
        ('picked', 'Đã lấy hàng'),
        ('shipping', 'Đang giao'),
        ('delivered', 'Đã giao'),
        ('failed', 'Giao thất bại'),
        ('cancelled', 'Đã huỷ'),
    ]

    order_id = models.IntegerField()
    customer_id = models.IntegerField()

    receiver_name = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=50, blank=True, default='')
    address = models.TextField(blank=True, default='')

    carrier = models.CharField(max_length=100, blank=True, default='')
    tracking_number = models.CharField(max_length=100, blank=True, default='')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment #{self.id} - Order {self.order_id}"

