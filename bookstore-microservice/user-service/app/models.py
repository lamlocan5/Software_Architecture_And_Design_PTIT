from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user  = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profile')
    name  = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Staff(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    name       = models.CharField(max_length=255)
    email      = models.EmailField(unique=True)
    active     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Manager(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='manager_profile')
    name       = models.CharField(max_length=255)
    email      = models.EmailField(unique=True)
    active     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
