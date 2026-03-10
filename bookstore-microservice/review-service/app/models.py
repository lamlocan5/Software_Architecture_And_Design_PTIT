from django.db import models


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 → 5 sao

    book_id       = models.IntegerField()
    customer_id   = models.IntegerField()
    customer_name = models.CharField(max_length=255, default='Khách hàng')
    book_title    = models.CharField(max_length=255, default='')
    rating        = models.IntegerField(choices=RATING_CHOICES)
    comment       = models.TextField(blank=True, default='')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review Book#{self.book_id} by Customer#{self.customer_id} — {self.rating}★"
