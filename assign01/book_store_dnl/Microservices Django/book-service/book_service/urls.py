"""URL Configuration for book-service"""
from django.contrib import admin
from django.urls import path
from books import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/books/', views.list_books, name='list_books'),
    path('api/books/<int:book_id>/', views.get_book, name='get_book'),
    path('api/books/<int:book_id>/stock/', views.update_stock, name='update_stock'),
    path('api/books/check-stock/', views.check_stock, name='check_stock'),
]
