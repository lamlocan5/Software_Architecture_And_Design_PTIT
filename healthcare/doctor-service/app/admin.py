from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'specialty', 'phone', 'email', 'created_at']
    search_fields = ['full_name', 'specialty', 'phone']
