"""
Store URLs: Product list/detail, Cart, Checkout.
"""
from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('book/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update_quantity, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/success/', views.order_success, name='order_success'),
]
