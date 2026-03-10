from django.db import models
from orders.models import Order

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)

    def process_payment(self):
        # giả lập thanh toán thành công
        self.status = "SUCCESS"
        self.save()

    def confirm_payment(self):
        return self.status == "SUCCESS"
