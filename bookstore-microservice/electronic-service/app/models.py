from django.db import models


class ElectronicCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class Electronic(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, default='')
    model = models.CharField(max_length=255, blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(
        ElectronicCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='electronics',
    )

    def __str__(self):
        return self.name

