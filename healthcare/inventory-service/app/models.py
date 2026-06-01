from django.db import models


class Medicine(models.Model):
    name = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=50)   # viên, chai, ống...
    stock = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medicines'

    def __str__(self):
        return f"{self.name} ({self.unit}) - Tồn: {self.stock}"


class StockTransaction(models.Model):
    TYPE_CHOICES = [
        ('import', 'Import'),
        ('export', 'Export'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    reference_id = models.CharField(max_length=255, blank=True, null=True)  # prescription_id từ clinical
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_transactions'

    def __str__(self):
        return f"{self.transaction_type.upper()} {self.quantity}x {self.medicine.name}"
