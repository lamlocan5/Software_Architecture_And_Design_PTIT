from django.contrib import admin
from .models import Appointment, Prescription, PrescriptionItem


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'doctor_id', 'scheduled_at', 'status', 'created_at']
    list_filter = ['status']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_id', 'appointment', 'diagnosis', 'created_at']


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'prescription', 'medicine_name', 'quantity', 'dosage']
