from django.urls import path
from gateway.views import (
    ProductsProxy, ProductDetailProxy, ProductsByIdsProxy,
    RecommendProxy, BehaviorProxy, ChatProxy, HealthCheckView
)

urlpatterns = [
    # Health check
    path('api/health/', HealthCheckView.as_view(), name='health'),
    # Products
    path('api/products/', ProductsProxy.as_view(), name='products'),
    path('api/products/by-ids/', ProductsByIdsProxy.as_view(), name='products-by-ids'),
    path('api/products/<int:pk>/', ProductDetailProxy.as_view(), name='product-detail'),
    # Recommend
    path('api/recommend/', RecommendProxy.as_view(), name='recommend'),
    # Behavior
    path('api/behaviors/', BehaviorProxy.as_view(), name='behavior'),
    # Chat
    path('api/chat/', ChatProxy.as_view(), name='chat'),
]
