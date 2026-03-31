from django.db import models
class Moblie(models.Model):
    model_name = models.CharField(max_length=255)
    chipset = models.CharField(max_length=100)
    storage_gb = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
