"""
Staff URLs
Routes for staff dashboard and management
"""
from django.urls import path
from store.controllers import staffController

urlpatterns = [
    path('login/', staffController.staff_login, name='staff_login'),
    path('logout/', staffController.staff_logout, name='staff_logout'),
    path('dashboard/', staffController.staff_dashboard, name='staff_dashboard'),
    path('orders/', staffController.manage_orders, name='manage_orders'),
    path('orders/<int:order_id>/update/', staffController.update_order_status, name='update_order_status'),
    path('inventory/', staffController.manage_inventory, name='manage_inventory'),
    path('inventory/<int:book_id>/update/', staffController.update_stock, name='update_stock'),
    path('customers/', staffController.manage_customers, name='manage_customers'),
    path('reports/sales/', staffController.sales_report, name='sales_report'),
]
