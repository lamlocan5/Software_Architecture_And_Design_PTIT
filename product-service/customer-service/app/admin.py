from django.contrib import admin
from .models import Customer, Cart, CartItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'full_name', 'created_at']
    search_fields = ['username', 'email']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['customer', 'created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product_name', 'product_type', 'quantity', 'price']
