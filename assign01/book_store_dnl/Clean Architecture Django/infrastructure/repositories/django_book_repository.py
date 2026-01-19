"""Django ORM implementation of BookRepository"""
from typing import List, Optional
from interfaces.repositories import BookRepository
from domain.entities.book import Book
from infrastructure.database.models import BookModel


class DjangoBookRepository(BookRepository):
    """Book repository using Django ORM"""
    
    def get_all(self) -> List[Book]:
        """Get all books from database"""
        book_models = BookModel.objects.all()
        return [self._to_entity(model) for model in book_models]
    
    def find_by_id(self, book_id: int) -> Optional[Book]:
        """Find book by ID"""
        try:
            book_model = BookModel.objects.get(id=book_id)
            return self._to_entity(book_model)
        except BookModel.DoesNotExist:
            return None
    
    def update(self, book: Book) -> Book:
        """Update book in database"""
        book_model = BookModel.objects.get(id=book.id)
        book_model.title = book.title
        book_model.author = book.author
        book_model.price = book.price
        book_model.stock = book.stock
        book_model.save()
        
        return self._to_entity(book_model)
    
    def _to_entity(self, model: BookModel) -> Book:
        """Convert Django model to domain entity"""
        return Book(
            id=model.id,
            title=model.title,
            author=model.author,
            price=model.price,
            stock=model.stock
        )
