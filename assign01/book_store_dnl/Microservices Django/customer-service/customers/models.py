from django.db import models


class Customer(models.Model):
    """Customer model for customer-service"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'accounts_customer'
    
    def __str__(self):
        return self.name
