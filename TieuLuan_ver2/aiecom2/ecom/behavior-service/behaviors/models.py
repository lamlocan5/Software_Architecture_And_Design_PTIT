from django.db import models


class UserProfile(models.Model):
    """500 user profiles (user_id 1-500)"""
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_profiles'


class UserBehavior(models.Model):
    """Hành vi người dùng: view, click, add_to_cart"""
    ACTION_CHOICES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('add_to_cart', 'Add to Cart'),
    ]
    user_id = models.IntegerField(db_index=True)
    product_id = models.IntegerField(db_index=True)  # Không FK, chỉ lưu ID
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'user_behaviors'
        ordering = ['user_id', 'timestamp']

    def __str__(self):
        return f"User {self.user_id} → {self.action} → Product {self.product_id}"
