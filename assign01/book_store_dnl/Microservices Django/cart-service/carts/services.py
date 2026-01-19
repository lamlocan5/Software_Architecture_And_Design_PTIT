"""Service clients for inter-service communication"""
import requests
import os


class CustomerServiceClient:
    """HTTP client for customer-service"""
    
    def __init__(self):
        self.base_url = os.getenv('CUSTOMER_SERVICE_URL', 'http://localhost:8001')
    
    def verify_customer(self, customer_id):
        """Verify that customer exists"""
        try:
            response = requests.get(f'{self.base_url}/api/customers/{customer_id}/', timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_customer(self, customer_id):
        """Get customer details"""
        try:
            response = requests.get(f'{self.base_url}/api/customers/{customer_id}/', timeout=5)
            if response.status_code == 200:
                return response.json().get('customer')
            return None
        except requests.RequestException:
            return None


class BookServiceClient:
    """HTTP client for book-service"""
    
    def __init__(self):
        self.base_url = os.getenv('BOOK_SERVICE_URL', 'http://localhost:8002')
    
    def get_book(self, book_id):
        """Get book details"""
        try:
            response = requests.get(f'{self.base_url}/api/books/{book_id}/', timeout=5)
            if response.status_code == 200:
                return response.json().get('book')
            return None
        except requests.RequestException:
            return None
    
    def check_stock(self, book_id, quantity):
        """Check if book has sufficient stock"""
        try:
            book = self.get_book(book_id)
            if book:
                return book['stock'] >= quantity
            return False
        except Exception:
            return False
    
    def update_stock(self, book_id, quantity, operation='reduce'):
        """Update book stock"""
        try:
            response = requests.patch(
                f'{self.base_url}/api/books/{book_id}/stock/',
                json={'quantity': quantity, 'operation': operation},
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
