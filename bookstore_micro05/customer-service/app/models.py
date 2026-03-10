from django.db import models

# Create your models here.
class Customer (models.Model):  #Lam recently added
    name = models.CharField(max_length =255)
    email = models.EmailField(unique = True)