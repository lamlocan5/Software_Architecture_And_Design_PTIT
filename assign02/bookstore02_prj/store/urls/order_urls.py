"""
Order URLs
Routes for cart, checkout, orders, and wishlist
"""
from django.urls import path
from store.controllers import orderController

urlpatterns = [
    # Cart
    path('', orderController.view_cart, name='view_cart'),
    path('add/<int:book_id>/', orderController.add_to_cart, name='add_to_cart'),
    path('update/<int:cart_id>/', orderController.update_cart, name='update_cart'),
    path('remove/<int:cart_id>/', orderController.remove_from_cart, name='remove_from_cart'),
    
    # Checkout and Orders
    path('checkout/', orderController.checkout, name='checkout'),
    path('orders/', orderController.order_history, name='order_history'),
    path('orders/<int:order_id>/', orderController.order_detail, name='order_detail'),
    
    # Wishlist
    path('wishlist/', orderController.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:book_id>/', orderController.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_id>/', orderController.remove_from_wishlist, name='remove_from_wishlist'),
]
