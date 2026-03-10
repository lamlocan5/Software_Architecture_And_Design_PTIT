"""
Staff related models
Based on database schema: Staff table
"""
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Staff(models.Model):
    """
    Staff model representing bookstore employees
    """
    ROLE_CHOICES = [
        ('Admin', 'Administrator'),
        ('Manager', 'Manager'),
        ('Sales', 'Sales Staff'),
        ('Support', 'Customer Support'),
    ]
    
    staff_id = models.AutoField(primary_key=True, db_column='StaffID')
    username = models.CharField(max_length=50, unique=True, db_column='Username')
    password = models.CharField(max_length=255, db_column='Password')
    email = models.EmailField(max_length=100, unique=True, db_column='Email')
    full_name = models.CharField(max_length=100, db_column='FullName')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Sales', db_column='Role')
    hire_date = models.DateField(auto_now_add=True, db_column='HireDate')
    
    class Meta:
        db_table = 'Staff'
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        ordering = ['hire_date']
    
    def __str__(self):
        return f"{self.username} - {self.role}"
    
    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if provided password matches"""
        return check_password(raw_password, self.password)
