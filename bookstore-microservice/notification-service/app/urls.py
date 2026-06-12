from django.urls import path
from .views import NotificationList, CustomerNotifications

urlpatterns = [
    path('notifications/', NotificationList.as_view(), name='notification_list'),
    path('notifications/customer/<int:customer_id>/', CustomerNotifications.as_view(), name='customer_notifications'),
]
