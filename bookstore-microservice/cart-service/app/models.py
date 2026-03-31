from django.db import models

# Create your models here.
class Cart(models.Model):

    customer_id = models.IntegerField()

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # Hỗ trợ sách (book-service), quần áo (clothe-service), điện tử (electronic-service)
    book_id = models.IntegerField(null=True, blank=True)
    clothing_id = models.IntegerField(null=True, blank=True)
    electronic_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField()