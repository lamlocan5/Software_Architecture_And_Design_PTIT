from django.urls import path
from . import views

urlpatterns = [
    path('', views.laptop_list, name='laptop-list'),
    path('<int:pk>/', views.laptop_detail, name='laptop-detail'),
    path('search/', views.laptop_search, name='laptop-search'),
]
