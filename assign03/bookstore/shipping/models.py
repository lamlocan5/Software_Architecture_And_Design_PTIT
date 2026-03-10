from django.db import models
from orders.models import Order

class DeliveryStaff(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Shipment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    delivery_staff = models.ForeignKey(DeliveryStaff, on_delete=models.SET_NULL, null=True)

    def update_status(self, status):
        self.status = status
        self.save()
