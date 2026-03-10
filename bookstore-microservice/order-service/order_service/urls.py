from django.contrib import admin
from django.urls import path
from app.views import OrderList, OrderCreate, OrderDetail, OrderStatusUpdate, CustomerOrders

urlpatterns = [
    path('admin/', admin.site.urls),

    path('orders/', OrderList.as_view()),
    path('orders/create/', OrderCreate.as_view()),
    path('orders/<int:order_id>/', OrderDetail.as_view()),
    path('orders/<int:order_id>/status/', OrderStatusUpdate.as_view()),
    path('orders/customer/<int:customer_id>/', CustomerOrders.as_view()),
]
