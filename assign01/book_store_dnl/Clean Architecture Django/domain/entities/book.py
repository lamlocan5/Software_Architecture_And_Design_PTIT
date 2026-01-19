"""Book entity - Core business logic for book domain"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    """Book entity with inventory management logic"""
    
    id: Optional[int]
    title: str
    author: str
    price: float
    stock: int
    
    def __post_init__(self):
        """Validate book data"""
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Book title cannot be empty")
        
        if not self.author or len(self.author.strip()) == 0:
            raise ValueError("Book author cannot be empty")
        
        if self.price <= 0:
            raise ValueError("Book price must be positive")
        
        if self.stock < 0:
            raise ValueError("Book stock cannot be negative")
    
    def is_in_stock(self, quantity: int = 1) -> bool:
        """Check if the requested quantity is available in stock"""
        return self.stock >= quantity
    
    def reduce_stock(self, quantity: int) -> None:
        """Reduce stock by the specified quantity"""
        if not self.is_in_stock(quantity):
            raise ValueError(f"Insufficient stock. Available: {self.stock}, Requested: {quantity}")
        
        self.stock -= quantity
    
    def increase_stock(self, quantity: int) -> None:
        """Increase stock by the specified quantity"""
        if quantity <= 0:
            raise ValueError("Quantity to increase must be positive")
        
        self.stock += quantity
    
    def calculate_total_price(self, quantity: int) -> float:
        """Calculate total price for given quantity"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        return self.price * quantity
