from django.shortcuts import render
from .models import Book
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Book Store")

def book_list(request):
    books = Book.objects.all()
    return render(request, 'books/book_list.html', {'books': books})
