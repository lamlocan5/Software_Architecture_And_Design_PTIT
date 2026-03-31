from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('cart/', views.cart_view, name='cart'),
    path('staff-login/', views.staff_login_view, name='staff_login'),
    path('products/', views.products_view, name='products'),
    path('product/<int:id>/', views.product_detail_view, name='product_detail'),
    path('profile/', views.profile_view, name='profile'),
    path('staff/dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/products/', views.manage_products_view, name='manage_products'),
    path('staff/orders/', views.manage_orders_view, name='manage_orders'),
]
