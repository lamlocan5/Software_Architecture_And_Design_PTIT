from django.db import models


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient_id = models.IntegerField()  # Logical FK → patient-service (không physical)
    doctor_id = models.IntegerField()  # Logical FK → doctor-service (không physical)
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointments'

    def __str__(self):
        return f"Appointment {self.id} - Patient {self.patient_id}"


class Prescription(models.Model):
    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='prescriptions'
    )
    patient_id = models.IntegerField()  # Logical FK → patient-service
    diagnosis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prescriptions'

    def __str__(self):
        return f"Prescription {self.id} for Patient {self.patient_id}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name='items'
    )
    medicine_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    dosage = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'prescription_items'

    def __str__(self):
        return f"{self.medicine_name} x{self.quantity}"
