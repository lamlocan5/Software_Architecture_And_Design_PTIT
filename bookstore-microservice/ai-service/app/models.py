from django.db import models

class UserBehavior(models.Model):
    user_id = models.IntegerField(db_index=True)
    product_id = models.IntegerField(db_index=True)
    behavior_type = models.CharField(max_length=20, db_index=True) # e.g. 'view', 'buy', 'cart'
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"User {self.user_id} - {self.behavior_type} - Product {self.product_id}"


class ProductNode(models.Model):
    product_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    product_type = models.CharField(max_length=50, default='book')

    def __str__(self):
        return f"Product {self.product_id}: {self.title}"


class ProductSimilarity(models.Model):
    product_id_1 = models.IntegerField(db_index=True)
    product_id_2 = models.IntegerField(db_index=True)
    similarity_score = models.FloatField()

    class Meta:
        unique_together = (('product_id_1', 'product_id_2'),)

    def __str__(self):
        return f"Prod {self.product_id_1} <-> Prod {self.product_id_2}: {self.similarity_score}"
