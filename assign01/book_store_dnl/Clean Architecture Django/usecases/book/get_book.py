"""Use case: Get book by ID"""
from typing import Protocol
from domain.entities.book import Book


class BookRepository(Protocol):
    """Repository interface for book data access"""
    
    def find_by_id(self, book_id: int) -> Book | None:
        """Find book by ID"""
        ...


class GetBook:
    """Use case for retrieving a single book"""
    
    def __init__(self, book_repository: BookRepository):
        self.book_repository = book_repository
    
    def execute(self, book_id: int) -> dict:
        """
        Get book by ID
        
        Args:
            book_id: Book ID
        
        Returns:
            dict with book data or error
        """
        book = self.book_repository.find_by_id(book_id)
        
        if not book:
            return {
                'success': False,
                'error': 'Book not found'
            }
        
        return {
            'success': True,
            'book': book
        }
