from django.contrib import admin
from django.urls import path

from app.views import (
    PaymentList,
    PaymentCreate,
    PaymentDetail,
    PaymentStatusUpdate,
    OrderPayments,
    CustomerPayments,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('payments/', PaymentList.as_view()),
    path('payments/create/', PaymentCreate.as_view()),
    path('payments/<int:payment_id>/', PaymentDetail.as_view()),
    path('payments/<int:payment_id>/status/', PaymentStatusUpdate.as_view()),
    path('payments/order/<int:order_id>/', OrderPayments.as_view()),
    path('payments/customer/<int:customer_id>/', CustomerPayments.as_view()),
]

