import requests
from django.conf import settings

class BaseService:
    def _get(self, url, params=None):
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None

    def _post(self, url, data=None):
        try:
            response = requests.post(url, json=data, timeout=5)
            return response.json(), response.status_code
        except requests.RequestException:
            return {'success': False, 'error': 'Service unavailable'}, 503
            
    def _delete(self, url):
        try:
            response = requests.delete(url, timeout=5)
            return response.json(), response.status_code
        except requests.RequestException:
            return {'success': False, 'error': 'Service unavailable'}, 503

class BookService(BaseService):
    def __init__(self):
        self.base_url = settings.SERVICE_URLS['BOOK']

    def list_books(self):
        data = self._get(f'{self.base_url}/books/')
        return data if data else {'books': [], 'count': 0}

    def get_book(self, book_id):
        return self._get(f'{self.base_url}/books/{book_id}/')

class CustomerService(BaseService):
    def __init__(self):
        self.base_url = settings.SERVICE_URLS['CUSTOMER']

    def login(self, email, password):
        return self._post(f'{self.base_url}/login/', {
            'email': email,
            'password': password
        })

    def register(self, name, email, password):
        return self._post(f'{self.base_url}/register/', {
            'name': name,
            'email': email,
            'password': password
        })

class CartService(BaseService):
    def __init__(self):
        self.base_url = settings.SERVICE_URLS['CART']

    def get_cart(self, customer_id):
        return self._get(f'{self.base_url}/cart/{customer_id}/')

    def add_to_cart(self, customer_id, book_id, quantity):
        return self._post(f'{self.base_url}/cart/add/', {
            'customer_id': customer_id,
            'book_id': book_id,
            'quantity': quantity
        })

    def remove_from_cart(self, item_id):
        return self._delete(f'{self.base_url}/cart/items/{item_id}/')
