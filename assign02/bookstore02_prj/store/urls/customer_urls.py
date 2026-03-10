"""
Customer URLs
Routes for customer registration, login, profile management
"""
from django.urls import path
from store.controllers import customerController

urlpatterns = [
    path('register/', customerController.register, name='customer_register'),
    path('login/', customerController.login, name='customer_login'),
    path('logout/', customerController.logout, name='customer_logout'),
    path('profile/', customerController.profile, name='customer_profile'),
    path('address/add/', customerController.add_address, name='add_address'),
    path('address/delete/<int:address_id>/', customerController.delete_address, name='delete_address'),
]
