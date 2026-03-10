"""
Customer related models
Based on database schema: Customer and Address tables
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Customer(models.Model):
    """
    Customer model representing registered users
    """
    customer_id = models.AutoField(primary_key=True, db_column='CustomerID')
    username = models.CharField(max_length=50, unique=True, db_column='Username')
    email = models.EmailField(max_length=100, unique=True, db_column='Email')
    password = models.CharField(max_length=255, db_column='Password')
    full_name = models.CharField(max_length=100, db_column='FullName')
    phone = models.CharField(max_length=20, blank=True, null=True, db_column='Phone')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, db_column='Avatar')
    
    class Meta:
        db_table = 'Customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return f"{self.username} - {self.full_name}"
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if provided password matches"""
        return check_password(raw_password, self.password)


class Address(models.Model):
    """
    Address model for customer shipping addresses
    """
    address_id = models.AutoField(primary_key=True, db_column='AddressID')
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses',
        db_column='CustomerID'
    )
    street = models.CharField(max_length=255, db_column='Street')
    city = models.CharField(max_length=100, db_column='City')
    country = models.CharField(max_length=100, db_column='Country')
    postal_code = models.CharField(max_length=20, db_column='PostalCode')
    
    class Meta:
        db_table = 'Address'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
    
    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"
