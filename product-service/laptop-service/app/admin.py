from django.contrib import admin
from .models import Laptop

@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'stock', 'created_at']
    search_fields = ['name', 'brand']
    list_filter = ['brand']
