from django.urls import path
from . import views

urlpatterns = [
    path('', views.mobile_list, name='mobile-list'),
    path('<int:pk>/', views.mobile_detail, name='mobile-detail'),
    path('search/', views.mobile_search, name='mobile-search'),
]
