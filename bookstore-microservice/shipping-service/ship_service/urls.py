from django.contrib import admin
from django.urls import path

from app.views import (
    ShipmentList,
    ShipmentCreate,
    ShipmentDetail,
    ShipmentStatusUpdate,
    OrderShipments,
    CustomerShipments,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('shipments/', ShipmentList.as_view()),
    path('shipments/create/', ShipmentCreate.as_view()),
    path('shipments/<int:shipment_id>/', ShipmentDetail.as_view()),
    path('shipments/<int:shipment_id>/status/', ShipmentStatusUpdate.as_view()),
    path('shipments/order/<int:order_id>/', OrderShipments.as_view()),
    path('shipments/customer/<int:customer_id>/', CustomerShipments.as_view()),
]

