from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.customer_register, name='customer-register'),
    path('login/', views.customer_login, name='customer-login'),
    # Token verify (dùng bởi internal services)
    path('verify/', views.verify_token, name='customer-verify'),

    # Search
    path('search/', views.search_products, name='customer-search'),

    # Cart
    path('cart/', views.get_cart, name='cart-get'),
    path('cart/add/', views.add_to_cart, name='cart-add'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='cart-remove'),
    path('cart/clear/', views.clear_cart, name='cart-clear'),
]
