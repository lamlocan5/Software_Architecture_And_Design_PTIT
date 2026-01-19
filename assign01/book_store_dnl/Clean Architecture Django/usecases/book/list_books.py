"""Use case: List all books"""
from typing import Protocol, List
from domain.entities.book import Book


class BookRepository(Protocol):
    """Repository interface for book data access"""
    
    def get_all(self) -> List[Book]:
        """Get all books"""
        ...


class ListBooks:
    """Use case for retrieving book catalog"""
    
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository
    
    def execute(self) -> dict:
        """
        Get all books from the catalog
        
        Returns:
            dict with list of books
        """
        books = self.book_repository.get_all()
        
        return {
            'success': True,
            'books': books,
            'count': len(books)
        }
