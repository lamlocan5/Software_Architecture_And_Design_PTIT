"""URL Configuration for cart-service"""
from django.contrib import admin
from django.urls import path
from carts import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/<int:customer_id>/', views.view_cart, name='view_cart'),
    path('api/cart/items/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/<int:customer_id>/clear/', views.clear_cart, name='clear_cart'),
]
