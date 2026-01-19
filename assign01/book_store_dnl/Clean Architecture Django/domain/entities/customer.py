"""Customer entity - Core business logic for customer domain"""
from dataclasses import dataclass
from typing import Optional
from django.contrib.auth.hashers import make_password, check_password


@dataclass
class Customer:
    """Customer entity with business logic"""
    
    id: Optional[int]
    name: str
    email: str
    _password: str
    
    def __post_init__(self):
        """Validate customer data"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Customer name cannot be empty")
        
        if not self.email or '@' not in self.email:
            raise ValueError("Invalid email format")
    
    @classmethod
    def create(cls, name: str, email: str, password: str) -> 'Customer':
        """Factory method to create a new customer"""
        # Monolith uses plain text password
        return cls(
            id=None,
            name=name,
            email=email,
            _password=password
        )
    
    def verify_password(self, password: str) -> bool:
        """Verify password (plain text comparison compatibility)"""
        return self._password == password
    
    def change_password(self, new_password: str) -> None:
        """Change customer password"""
        if not new_password or len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters")
        self._password = new_password
    
    @property
    def password(self) -> str:
        """Get password (read-only)"""
        return self._password
