from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    description = models.TextField()
    image_url = models.URLField(blank=True, default='')

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"[{self.id}] {self.name}"
