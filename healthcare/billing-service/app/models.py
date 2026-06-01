from django.db import models


class Bill(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    patient_id = models.IntegerField()       # Logical FK → patient-service
    prescription_id = models.IntegerField(null=True, blank=True)  # Logical FK → clinical-service
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'bills'

    def __str__(self):
        return f"Bill {self.id} - Patient {self.patient_id} - {self.status}"

    def recalculate_total(self):
        """Tính lại total_amount từ các BillItem."""
        from decimal import Decimal
        total = sum(
            item.unit_price * item.quantity for item in self.items.all()
        )
        self.total_amount = total
        self.save(update_fields=['total_amount'])


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'bill_items'

    def __str__(self):
        return f"{self.description} x{self.quantity} @ {self.unit_price}"
