from django.contrib import admin
from .models import Mobile

@admin.register(Mobile)
class MobileAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'price', 'stock', 'created_at']
    search_fields = ['name', 'brand']
    list_filter = ['brand', 'os']
