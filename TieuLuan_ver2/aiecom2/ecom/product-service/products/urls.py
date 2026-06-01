from django.urls import path
from .views import ProductListView, ProductDetailView, ProductsByIdsView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/by-ids/', ProductsByIdsView.as_view(), name='products-by-ids'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
