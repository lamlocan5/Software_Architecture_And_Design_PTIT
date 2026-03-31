from django.db import models
class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
class CustomerAccount(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
class Cart(models.Model):
    account = models.ForeignKey(CustomerAccount, on_delete=models.CASCADE, related_name="carts")
    name = models.CharField(max_length=100, default="default")
    is_active = models.BooleanField(default=True)
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_type = models.CharField(max_length=20)
    product_id = models.PositiveIntegerField()
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
