"""
Book URLs
Routes for book browsing, searching, and reviews
"""
from django.urls import path
from store.controllers import bookController

urlpatterns = [
    path('', bookController.book_list, name='book_list'),
    path('book/<int:book_id>/', bookController.book_detail, name='book_detail'),
    path('search/', bookController.search_books, name='search_books'),
    path('category/<int:category_id>/', bookController.books_by_category, name='books_by_category'),
    path('author/<int:author_id>/', bookController.books_by_author, name='books_by_author'),
    path('book/<int:book_id>/review/', bookController.add_review, name='add_review'),
]
