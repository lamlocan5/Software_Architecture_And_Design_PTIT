from django.db import models

class Notification(models.Model):
    customer_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=50, default='system')  # 'email', 'sms', 'system'
    status = models.CharField(max_length=50, default='sent')    # 'sent', 'failed'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.type.upper()}] {self.title} (customer_id={self.customer_id})"
