"""Cart entities - Core business logic for shopping cart domain"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class CartItem:
    """Cart item entity"""
    
    id: Optional[int]
    book_id: int
    book_title: str
    book_price: float
    quantity: int
    
    def __post_init__(self):
        """Validate cart item data"""
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.book_price <= 0:
            raise ValueError("Book price must be positive")
    
    def calculate_subtotal(self) -> float:
        """Calculate subtotal for this item"""
        return self.book_price * self.quantity
    
    def update_quantity(self, new_quantity: int) -> None:
        """Update item quantity"""
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")
        self.quantity = new_quantity


@dataclass
class Cart:
    """Shopping cart entity with business logic"""
    
    id: Optional[int]
    customer_id: int
    items: List[CartItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    
    def add_item(self, book_id: int, book_title: str, book_price: float, quantity: int) -> None:
        """Add item to cart or update quantity if already exists"""
        # Check if item already exists
        for item in self.items:
            if item.book_id == book_id:
                item.update_quantity(item.quantity + quantity)
                return
        
        # Add new item
        new_item = CartItem(
            id=None,
            book_id=book_id,
            book_title=book_title,
            book_price=book_price,
            quantity=quantity
        )
        self.items.append(new_item)
    
    def remove_item(self, book_id: int) -> None:
        """Remove item from cart"""
        self.items = [item for item in self.items if item.book_id != book_id]
    
    def update_item_quantity(self, book_id: int, new_quantity: int) -> None:
        """Update quantity of a specific item"""
        for item in self.items:
            if item.book_id == book_id:
                item.update_quantity(new_quantity)
                return
        raise ValueError(f"Item with book_id {book_id} not found in cart")
    
    def calculate_total(self) -> float:
        """Calculate total price of all items in cart"""
        return sum(item.calculate_subtotal() for item in self.items)
    
    def get_item_count(self) -> int:
        """Get total number of items in cart"""
        return len(self.items)
    
    def clear(self) -> None:
        """Remove all items from cart"""
        self.items.clear()
    
    def is_empty(self) -> bool:
        """Check if cart is empty"""
        return len(self.items) == 0
