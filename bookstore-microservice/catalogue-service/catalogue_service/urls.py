from django.contrib import admin
from django.urls import path
from app.views import CatalogueBookList, CatalogueBookDetail

urlpatterns = [
    path('admin/', admin.site.urls),

    path('catalog/books/', CatalogueBookList.as_view()),
    path('catalog/books/<int:pk>/', CatalogueBookDetail.as_view()),
]


