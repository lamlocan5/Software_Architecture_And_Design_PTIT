from django.db import models

class Publisher(models.Model):
    name    = models.CharField(max_length=255)
    address = models.TextField(blank=True, default='')
    mail    = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    # category_type to distinguish 'clothing' categories from 'electronic' categories
    category_type = models.CharField(max_length=50, default='clothing')

    def __str__(self):
        return f"{self.name} ({self.category_type})"

class Product(models.Model):
    PRODUCT_TYPES = [
        ('book', 'Sách'),
        ('clothing', 'Thời trang'),
        ('electronic', 'Điện tử'),
    ]
    name         = models.CharField(max_length=255)
    product_type = models.CharField(max_length=50, choices=PRODUCT_TYPES)
    price        = models.DecimalField(max_digits=12, decimal_places=2)
    stock        = models.IntegerField()
    # Flexible attributes stored as JSON
    attributes   = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"[{self.product_type}] {self.name}"
