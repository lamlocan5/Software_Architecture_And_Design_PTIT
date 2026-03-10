"""
Order and shopping related models
Based on database schema: Order, OrderItem, Cart, Wishlist, Shipping tables
"""
from django.db import models
from django.utils import timezone
from .customer import Customer
from .book import Book


class Order(models.Model):
    """
    Order model representing customer orders
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('E-Wallet', 'E-Wallet'),
    ]
    
    order_id = models.AutoField(primary_key=True, db_column='OrderID')
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        db_column='CustomerID'
    )
    order_date = models.DateTimeField(default=timezone.now, db_column='OrderDate')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, db_column='TotalAmount')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', db_column='Status')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, db_column='PaymentMethod')
    
    class Meta:
        db_table = 'Order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Order #{self.order_id} - {self.customer.username}"
    
    def calculate_total(self):
        """Calculate total amount from order items"""
        total = sum(item.price * item.quantity for item in self.items.all())
        self.total_amount = total
        return total


class OrderItem(models.Model):
    """
    OrderItem model representing individual items in an order
    """
    order_item_id = models.AutoField(primary_key=True, db_column='OrderItemID')
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='OrderID'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='order_items',
        db_column='BookID'
    )
    quantity = models.IntegerField(default=1, db_column='Quantity')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='Price')
    
    class Meta:
        db_table = 'OrderItem'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def __str__(self):
        return f"{self.book.title} x {self.quantity}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.price * self.quantity


class Cart(models.Model):
    """
    Shopping cart model
    """
    cart_id = models.AutoField(primary_key=True, db_column='CartID')
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='cart_items',
        db_column='CustomerID'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='in_carts',
        db_column='BookID'
    )
    quantity = models.IntegerField(default=1, db_column='Quantity')
    added_at = models.DateTimeField(auto_now_add=True, db_column='AddedAt')
    
    class Meta:
        db_table = 'Cart'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('customer', 'book')
    
    def __str__(self):
        return f"{self.customer.username} - {self.book.title}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.book.price * self.quantity


class Wishlist(models.Model):
    """
    Wishlist model for customer's desired books
    """
    wishlist_id = models.AutoField(primary_key=True, db_column='WishlistID')
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        db_column='CustomerID'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='in_wishlists',
        db_column='BookID'
    )
    added_at = models.DateTimeField(auto_now_add=True, db_column='AddedAt')
    
    class Meta:
        db_table = 'Wishlist'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ('customer', 'book')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.customer.username} - {self.book.title}"


class Shipping(models.Model):
    """
    Shipping information for orders
    """
    SHIPPING_METHODS = [
        ('Standard', 'Standard Shipping'),
        ('Express', 'Express Shipping'),
        ('Overnight', 'Overnight Shipping'),
    ]
    
    shipping_id = models.AutoField(primary_key=True, db_column='ShippingID')
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='shipping',
        db_column='OrderID'
    )
    address = models.ForeignKey(
        'Address',
        on_delete=models.SET_NULL,
        null=True,
        related_name='shipments',
        db_column='AddressID'
    )
    shipping_method = models.CharField(
        max_length=50,
        choices=SHIPPING_METHODS,
        default='Standard',
        db_column='ShippingMethod'
    )
    tracking_number = models.CharField(max_length=100, blank=True, null=True, db_column='TrackingNumber')
    estimated_delivery = models.DateField(blank=True, null=True, db_column='EstimatedDelivery')
    
    class Meta:
        db_table = 'Shipping'
        verbose_name = 'Shipping'
        verbose_name_plural = 'Shippings'
    
    def __str__(self):
        return f"Shipping for Order #{self.order.order_id}"
