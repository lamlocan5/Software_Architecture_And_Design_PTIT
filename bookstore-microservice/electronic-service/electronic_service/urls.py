from django.contrib import admin
from django.urls import path
from app.views import ElectronicListCreate, ElectronicDetail, ElectronicCategoryListCreate, ElectronicCategoryDetail

urlpatterns = [
    path('admin/', admin.site.urls),

    path('electronics/', ElectronicListCreate.as_view()),
    path('electronics/<int:pk>/', ElectronicDetail.as_view()),
    path('electronics/categories/', ElectronicCategoryListCreate.as_view()),
    path('electronics/categories/<int:pk>/', ElectronicCategoryDetail.as_view()),
]

