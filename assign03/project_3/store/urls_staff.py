"""
Staff URLs: Dashboard, Book create.
"""
from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('dashboard/', views.staff_dashboard, name='dashboard'),
    path('books/add/', views.StaffBookCreateView.as_view(), name='book_add'),
]
