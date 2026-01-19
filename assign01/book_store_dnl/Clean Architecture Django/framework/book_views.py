"""Django views for book operations"""
from django.shortcuts import render
from django.http import HttpResponse

from usecases.book.list_books import ListBooks
from usecases.book.get_book import GetBook
from infrastructure.repositories.django_book_repository import DjangoBookRepository


# Initialize repository
book_repository = DjangoBookRepository()


def home_view(request):
    """Home page view"""
    return render(request, 'home.html')


def book_list_view(request):
    """Book list view"""
    # Execute use case
    use_case = ListBooks(book_repository)
    result = use_case.execute()
    
    context = {
        'books': result['books'],
        'count': result['count']
    }
    
    return render(request, 'books/book_list.html', context)


def book_detail_view(request, book_id):
    """Book detail view"""
    # Execute use case
    use_case = GetBook(book_repository)
    result = use_case.execute(book_id)
    
    if result['success']:
        context = {'book': result['book']}
        return render(request, 'books/book_detail.html', context)
    else:
        return HttpResponse(result['error'], status=404)
