from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeductStockInternalView, MedicineViewSet, StockTransactionViewSet

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet, basename='medicine')
router.register(r'stock-transactions', StockTransactionViewSet, basename='stock-transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('internal/deduct-stock/', DeductStockInternalView.as_view(), name='internal-deduct-stock'),
]
