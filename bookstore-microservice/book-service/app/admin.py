from django.contrib import admin
from .models import Book, Publisher

admin.site.register(Publisher)
admin.site.register(Book)
