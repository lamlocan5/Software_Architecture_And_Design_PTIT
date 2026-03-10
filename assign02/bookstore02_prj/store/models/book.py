"""
Book catalog related models
Based on database schema: Book, Author, Publisher, Category, and related tables
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    """
    Author model representing book authors
    """
    author_id = models.AutoField(primary_key=True, db_column='AuthorID')
    name = models.CharField(max_length=100, db_column='Name')
    biography = models.TextField(blank=True, null=True, db_column='Biography')
    
    class Meta:
        db_table = 'Author'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
    
    def __str__(self):
        return self.name


class Publisher(models.Model):
    """
    Publisher model representing book publishers
    """
    publisher_id = models.AutoField(primary_key=True, db_column='PublisherID')
    name = models.CharField(max_length=100, db_column='Name')
    address = models.CharField(max_length=255, blank=True, null=True, db_column='Address')
    email = models.EmailField(max_length=100, blank=True, null=True, db_column='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, db_column='Phone')
    
    class Meta:
        db_table = 'Publisher'
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'
    
    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Category model for book categorization
    """
    category_id = models.AutoField(primary_key=True, db_column='CategoryID')
    name = models.CharField(max_length=100, db_column='Name')
    description = models.TextField(blank=True, null=True, db_column='Description')
    
    class Meta:
        db_table = 'Category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """
    Book model representing books in the catalog
    """
    book_id = models.AutoField(primary_key=True, db_column='BookID')
    title = models.CharField(max_length=255, db_column='Title')
    isbn = models.CharField(max_length=20, unique=True, db_column='ISBN')
    description = models.TextField(blank=True, null=True, db_column='Description')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='Price')
    stock = models.IntegerField(default=0, db_column='Stock')
    published_date = models.DateField(blank=True, null=True, db_column='PublishedDate')
    cover_image = models.ImageField(upload_to='books/', blank=True, null=True, db_column='CoverImage')
    
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        related_name='books',
        db_column='PublisherID'
    )
    
    # Many-to-many relationships
    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')
    categories = models.ManyToManyField(Category, through='BookCategory', related_name='books')
    
    class Meta:
        db_table = 'Book'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0


class BookAuthor(models.Model):
    """
    Junction table for Book-Author many-to-many relationship
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_column='AuthorID')
    
    class Meta:
        db_table = 'BookAuthor'
        unique_together = ('book', 'author')
        verbose_name = 'Book-Author Relationship'
        verbose_name_plural = 'Book-Author Relationships'
    
    def __str__(self):
        return f"{self.book.title} - {self.author.name}"


class BookCategory(models.Model):
    """
    Junction table for Book-Category many-to-many relationship
    """
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='CategoryID')
    
    class Meta:
        db_table = 'BookCategory'
        unique_together = ('book', 'category')
        verbose_name = 'Book-Category Relationship'
        verbose_name_plural = 'Book-Category Relationships'
    
    def __str__(self):
        return f"{self.book.title} - {self.category.name}"


class Review(models.Model):
    """
    Review model for customer book reviews
    """
    review_id = models.AutoField(primary_key=True, db_column='ReviewID')
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_column='BookID'
    )
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.CASCADE,
        related_name='reviews',
        db_column='CustomerID'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_column='Rating'
    )
    comment = models.TextField(blank=True, null=True, db_column='Comment')
    created_at = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')
    
    class Meta:
        db_table = 'Review'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('book', 'customer')  # One review per customer per book
    
    def __str__(self):
        return f"{self.customer.username} - {self.book.title} ({self.rating}★)"
