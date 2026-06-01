from django.db import models


class BehaviourLog(models.Model):
    """Ghi nhận từng hành vi của khách hàng"""
    ACTION_CHOICES = [
        ('view_product',     'Xem sản phẩm'),
        ('search',           'Tìm kiếm'),
        ('add_to_cart',      'Thêm vào giỏ'),
        ('remove_from_cart', 'Xóa khỏi giỏ'),
        ('checkout',         'Thanh toán'),
    ]
    customer_id  = models.IntegerField(db_index=True)
    product_id   = models.IntegerField()
    product_type = models.CharField(max_length=20)   # 'laptop' | 'mobile'
    product_name = models.CharField(max_length=255, blank=True)
    action       = models.CharField(max_length=30, choices=ACTION_CHOICES)
    search_query = models.CharField(max_length=255, blank=True)  # nếu action=search
    price        = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [models.Index(fields=['customer_id', 'product_type'])]


class UserProfile(models.Model):
    """Cache hồ sơ hành vi được tính từ BehaviourLog"""
    customer_id        = models.IntegerField(unique=True, db_index=True)
    laptop_score       = models.FloatField(default=0)
    mobile_score       = models.FloatField(default=0)
    budget_avg         = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preferred_brands   = models.JSONField(default=list)   # ['Dell', 'Apple', ...]
    preferred_usecases = models.JSONField(default=list)   # ['gaming', 'student', ...]
    top_products       = models.JSONField(default=list)   # [{id, type, name, score}, ...]
    total_events       = models.IntegerField(default=0)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'


class ChatHistory(models.Model):
    """Lưu lịch sử hội thoại tư vấn"""
    customer_id  = models.IntegerField(db_index=True)
    session_id   = models.CharField(max_length=64, db_index=True)
    role         = models.CharField(max_length=10)  # 'user' | 'assistant'
    content      = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
