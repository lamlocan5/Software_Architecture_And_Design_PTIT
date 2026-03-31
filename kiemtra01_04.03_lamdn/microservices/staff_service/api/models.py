from django.db import models
class Staff(models.Model):
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
class StaffAccount(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE)
