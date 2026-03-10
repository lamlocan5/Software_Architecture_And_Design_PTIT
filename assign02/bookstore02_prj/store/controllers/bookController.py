"""
Book Controller (Views)
Handles book listing, search, details, reviews
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.contrib import messages
from store.models.book import Book, Category, Author, Review
from store.models.customer import Customer


def book_list(request):
    """List all books with pagination and filters"""
    books = Book.objects.all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(categories__category_id=category_id)
    
    # Filter by author
    author_id = request.GET.get('author')
    if author_id:
        books = books.filter(authors__author_id=author_id)
    
    # Sort
    sort_by = request.GET.get('sort', '-published_date')
    books = books.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(books, 12)  # 12 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'books': page_obj,
        'categories': Category.objects.all(),
        'authors': Author.objects.all(),
        'search_query': search_query,
    }
    return render(request, 'book/list.html', context)


def book_detail(request, book_id):
    """Book detail page with reviews"""
    book = get_object_or_404(Book, book_id=book_id)
    reviews = book.reviews.all().order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if customer has already reviewed
    customer_id = request.session.get('customer_id')
    has_reviewed = False
    if customer_id:
        has_reviewed = reviews.filter(customer_id=customer_id).exists()
    
    context = {
        'book': book,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'has_reviewed': has_reviewed,
        'authors': book.authors.all(),
        'categories': book.categories.all(),
    }
    return render(request, 'book/detail.html', context)


def search_books(request):
    """Advanced book search"""
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    author = request.GET.get('author', '')
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 999999)
    
    books = Book.objects.all()
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(isbn__icontains=query)
        )
    
    if category:
        books = books.filter(categories__category_id=category)
    
    if author:
        books = books.filter(authors__author_id=author)
    
    books = books.filter(price__gte=min_price, price__lte=max_price)
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'books': page_obj,
        'categories': Category.objects.all(),
        'authors': Author.objects.all(),
        'query': query,
    }
    return render(request, 'book/search.html', context)


def add_review(request, book_id):
    """Add a review for a book"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        messages.error(request, 'Please login to add a review')
        return redirect('customer_login')
    
    book = get_object_or_404(Book, book_id=book_id)
    customer = get_object_or_404(Customer, customer_id=customer_id)
    
    # Check if already reviewed
    if Review.objects.filter(book=book, customer=customer).exists():
        messages.error(request, 'You have already reviewed this book')
        return redirect('book_detail', book_id=book_id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        review = Review(
            book=book,
            customer=customer,
            rating=rating,
            comment=comment
        )
        review.save()
        messages.success(request, 'Review added successfully')
        return redirect('book_detail', book_id=book_id)
    
    context = {'book': book}
    return render(request, 'book/add_review.html', context)


def books_by_category(request, category_id):
    """List books by category"""
    category = get_object_or_404(Category, category_id=category_id)
    books = Book.objects.filter(categories=category)
    
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'books': page_obj,
    }
    return render(request, 'book/category.html', context)


def books_by_author(request, author_id):
    """List books by author"""
    author = get_object_or_404(Author, author_id=author_id)
    books = Book.objects.filter(authors=author)
    
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'author': author,
        'books': page_obj,
    }
    return render(request, 'book/author.html', context)
