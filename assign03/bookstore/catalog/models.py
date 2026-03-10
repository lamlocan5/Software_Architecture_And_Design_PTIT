from django.db import models

class Publisher(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField()

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    publish_date = models.DateField()
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)

    def get_detail(self):
        return self

    def update_info(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

    def __str__(self):
        return self.title
