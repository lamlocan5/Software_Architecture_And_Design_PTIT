from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    customer_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username} (customer_id={self.customer_id})"
