"""URL Configuration for customer-service"""
from django.contrib import admin
from django.urls import path
from customers import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login, name='login'),
    path('api/customers/<int:customer_id>/', views.get_customer, name='get_customer'),
]
