from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class Clothing(models.Model):
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=50, blank=True, default='')
    color = models.CharField(max_length=50, blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clothes',
    )

    def __str__(self):
        return self.name

