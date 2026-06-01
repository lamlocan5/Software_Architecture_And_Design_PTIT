from django.contrib import admin
from .models import Bill, BillItem


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'prescription_id', 'total_amount', 'status', 'created_at', 'paid_at']
    list_filter = ['status']


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'bill', 'description', 'unit_price', 'quantity']
