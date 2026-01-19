"""Use case: Authenticate customer"""
from typing import Protocol
from domain.entities.customer import Customer


class CustomerRepository(Protocol):
    """Repository interface for customer data access"""
    
    def find_by_email(self, email: str) -> Customer | None:
        """Find customer by email"""
        ...


class AuthenticateCustomer:
    """Use case for customer authentication/login"""
    
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository
    
    def execute(self, email: str, password: str) -> dict:
        """
        Authenticate a customer
        
        Args:
            email: Customer email
            password: Customer password
        
        Returns:
            dict with success status and customer data or error
        """
        # Find customer by email
        customer = self.customer_repository.find_by_email(email)
        
        if not customer:
            return {
                'success': False,
                'error': 'Invalid email or password'
            }
        
        # Verify password
        if not customer.verify_password(password):
            return {
                'success': False,
                'error': 'Invalid email or password'
            }
        
        return {
            'success': True,
            'customer': customer,
            'message': 'Login successful'
        }
