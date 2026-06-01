from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BillViewSet, CreateBillInternalView

router = DefaultRouter()
router.register(r'bills', BillViewSet, basename='bill')

urlpatterns = [
    path('', include(router.urls)),
    path('internal/create-bill/', CreateBillInternalView.as_view(), name='internal-create-bill'),
]
