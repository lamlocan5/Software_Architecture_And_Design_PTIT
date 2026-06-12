from django.contrib import admin
from django.urls import path
from app.views import (
    BookListCreate, BookDetail, PublisherListCreate, PublisherDetail,
    ClothingListCreate, ClothingDetail, CategoryListCreate, CategoryDetail,
    ElectronicListCreate, ElectronicDetail, ElectronicCategoryListCreate, ElectronicCategoryDetail,
    ProductDetailGeneric
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Generic
    path('products/<int:pk>/', ProductDetailGeneric.as_view()),

    # Books
    path('books/', BookListCreate.as_view()),
    path('books/<int:pk>/', BookDetail.as_view()),
    path('publishers/', PublisherListCreate.as_view()),
    path('publishers/<int:pk>/', PublisherDetail.as_view()),

    # Clothes
    path('clothes/', ClothingListCreate.as_view()),
    path('clothes/<int:pk>/', ClothingDetail.as_view()),
    path('clothes/categories/', CategoryListCreate.as_view()),
    path('clothes/categories/<int:pk>/', CategoryDetail.as_view()),

    # Electronics
    path('electronics/', ElectronicListCreate.as_view()),
    path('electronics/<int:pk>/', ElectronicDetail.as_view()),
    path('electronics/categories/', ElectronicCategoryListCreate.as_view()),
    path('electronics/categories/<int:pk>/', ElectronicCategoryDetail.as_view()),
]
