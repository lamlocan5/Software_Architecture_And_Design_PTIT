from django.contrib import admin
from django.urls import path
from app.views import ClothingListCreate, ClothingDetail, CategoryListCreate, CategoryDetail

urlpatterns = [
    path('admin/', admin.site.urls),

    path('clothes/', ClothingListCreate.as_view()),
    path('clothes/<int:pk>/', ClothingDetail.as_view()),
    path('clothes/categories/', CategoryListCreate.as_view()),
    path('clothes/categories/<int:pk>/', CategoryDetail.as_view()),
]

