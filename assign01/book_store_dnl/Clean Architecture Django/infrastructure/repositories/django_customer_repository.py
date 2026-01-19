"""Django ORM implementation of CustomerRepository"""
from typing import Optional
from interfaces.repositories import CustomerRepository
from domain.entities.customer import Customer
from infrastructure.database.models import CustomerModel


class DjangoCustomerRepository(CustomerRepository):
    """Customer repository using Django ORM"""
    
    def create(self, customer: Customer) -> Customer:
        """Create new customer in database"""
        customer_model = CustomerModel.objects.create(
            name=customer.name,
            email=customer.email,
            password=customer.password
        )
        
        # Convert back to entity
        return Customer(
            id=customer_model.id,
            name=customer_model.name,
            email=customer_model.email,
            _password=customer_model.password
        )
    
    def find_by_email(self, email: str) -> Optional[Customer]:
        """Find customer by email"""
        try:
            customer_model = CustomerModel.objects.get(email=email)
            return self._to_entity(customer_model)
        except CustomerModel.DoesNotExist:
            return None
    
    def find_by_id(self, customer_id: int) -> Optional[Customer]:
        """Find customer by ID"""
        try:
            customer_model = CustomerModel.objects.get(id=customer_id)
            return self._to_entity(customer_model)
        except CustomerModel.DoesNotExist:
            return None
    
    def _to_entity(self, model: CustomerModel) -> Customer:
        """Convert Django model to domain entity"""
        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
            _password=model.password
        )
