from django.db import models


class Book(models.Model):
    """Book model for book-service"""
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    
    class Meta:
        db_table = 'books_book'
    
    def __str__(self):
        return self.title
