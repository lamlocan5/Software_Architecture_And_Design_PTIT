"""Use case: Register new customer"""
from typing import Protocol
from domain.entities.customer import Customer


class CustomerRepository(Protocol):
    """Repository interface for customer data access"""
    
    def find_by_email(self, email: str) -> Customer | None:
        """Find customer by email"""
        ...
    
    def create(self, customer: Customer) -> Customer:
        """Create new customer"""
        ...


class RegisterCustomer:
    """Use case for customer registration"""
    
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository
    
    def execute(self, name: str, email: str, password: str) -> dict:
        """
        Register a new customer
        
        Args:
            name: Customer name
            email: Customer email
            password: Customer password (will be hashed)
        
        Returns:
            dict with success status and message or error
        """
        # Business rule: Check if email already exists
        existing_customer = self.customer_repository.find_by_email(email)
        if existing_customer:
            return {
                'success': False,
                'error': 'Email already registered'
            }
        
        # Business rule: Password must be at least 6 characters
        if len(password) < 6:
            return {
                'success': False,
                'error': 'Password must be at least 6 characters'
            }
        
        try:
            # Create customer entity (password will be hashed)
            customer = Customer.create(name=name, email=email, password=password)
            
            # Save to repository
            saved_customer = self.customer_repository.create(customer)
            
            return {
                'success': True,
                'customer': saved_customer,
                'message': 'Registration successful'
            }
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
