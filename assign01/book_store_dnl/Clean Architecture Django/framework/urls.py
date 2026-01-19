"""URL Configuration for Clean Architecture Book Store"""
from django.contrib import admin
from django.urls import path
from framework import customer_views, book_views, cart_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home
    path('', book_views.home_view, name='home'),
    
    # Customer/Account URLs
    path('register/', customer_views.register_view, name='register'),
    path('login/', customer_views.login_view, name='login'),
    path('logout/', customer_views.logout_view, name='logout'),
    
    # Book URLs
    path('books/', book_views.book_list_view, name='book_list'),
    path('books/<int:book_id>/', book_views.book_detail_view, name='book_detail'),
    
    # Cart URLs
    path('cart/', cart_views.view_cart_view, name='view_cart'),
    path('cart/add/', cart_views.add_to_cart_view, name='add_to_cart'),
    path('cart/remove/', cart_views.remove_from_cart_view, name='remove_from_cart'),
]
