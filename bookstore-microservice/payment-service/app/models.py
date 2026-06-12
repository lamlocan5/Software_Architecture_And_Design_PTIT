from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ('initiated', 'Khởi tạo'),
        ('paid', 'Đã thanh toán'),
        ('failed', 'Thất bại'),
        ('refunded', 'Đã hoàn tiền'),
        ('cancelled', 'Đã huỷ'),
    ]

    METHOD_CHOICES = [
        ('cod', 'COD'),
        ('bank', 'Chuyển khoản'),
        ('card', 'Thẻ'),
        ('wallet', 'Ví điện tử'),
    ]

    order_id = models.IntegerField()
    customer_id = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='cod')
    provider = models.CharField(max_length=100, blank=True, default='')
    transaction_id = models.CharField(max_length=100, blank=True, default='')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.id} - Order {self.order_id}"

