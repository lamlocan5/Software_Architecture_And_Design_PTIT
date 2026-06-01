from django.contrib import admin
from .models import Staff

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'created_at']
    search_fields = ['username', 'email']
    list_filter = ['role']
