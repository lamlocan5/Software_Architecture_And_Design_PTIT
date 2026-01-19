"""Repository interfaces - Abstract contracts for data access"""
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.customer import Customer
from domain.entities.book import Book
from domain.entities.cart import Cart


class CustomerRepository(ABC):
    """Abstract repository for customer data access"""
    
    @abstractmethod
    def create(self, customer: Customer) -> Customer:
        """Create new customer"""
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find customer by email"""
        pass
    
    @abstractmethod
    def find_by_id(self, customer_id: int) -> Optional[Customer]:
        """Find customer by ID"""
        pass


class BookRepository(ABC):
    """Abstract repository for book data access"""
    
    @abstractmethod
    def get_all(self) -> List[Book]:
        """Get all books"""
        pass
    
    @abstractmethod
    def find_by_id(self, book_id: int) -> Optional[Book]:
        """Find book by ID"""
        pass
    
    @abstractmethod
    def update(self, book: Book) -> Book:
        """Update book"""
        pass


class CartRepository(ABC):
    """Abstract repository for cart data access"""
    
    @abstractmethod
    def get_or_create(self, customer_id: int) -> Cart:
        """Get or create cart for customer"""
        pass
    
    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Save cart"""
        pass
    
    @abstractmethod
    def delete_item(self, customer_id: int, book_id: int) -> None:
        """Delete specific item from cart"""
        pass
