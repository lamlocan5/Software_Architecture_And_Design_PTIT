from django.db import models


class Publisher(models.Model):
    name    = models.CharField(max_length=255)
    address = models.TextField(blank=True, default='')
    mail    = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title     = models.CharField(max_length=255)
    author    = models.CharField(max_length=255)
    price     = models.DecimalField(max_digits=10, decimal_places=2)
    stock     = models.IntegerField()
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
    )

    def __str__(self):
        return self.title