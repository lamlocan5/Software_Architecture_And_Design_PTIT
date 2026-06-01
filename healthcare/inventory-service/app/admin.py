from django.contrib import admin
from .models import Medicine, StockTransaction


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'unit', 'stock', 'unit_price', 'updated_at']
    search_fields = ['name']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'medicine', 'transaction_type', 'quantity', 'reference_id', 'created_at']
    list_filter = ['transaction_type']
