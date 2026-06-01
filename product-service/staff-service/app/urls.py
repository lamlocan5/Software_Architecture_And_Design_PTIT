from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.staff_register, name='staff-register'),
    path('login/', views.staff_login, name='staff-login'),
    path('profile/', views.staff_profile, name='staff-profile'),
    path('items/add/', views.add_item, name='add-item'),
    path('items/<str:item_type>/', views.list_items, name='list-items'),
    path('items/<str:item_type>/<int:pk>/update/', views.update_item, name='update-item'),
]
