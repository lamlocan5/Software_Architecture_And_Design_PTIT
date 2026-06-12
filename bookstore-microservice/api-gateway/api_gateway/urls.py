from django.contrib import admin
from django.urls import path
from api_gateway.views import (
    home,
    catalogue_list,
    cart_view,
    order_checkout,
    order_detail,
    notifications_api
)

from api_gateway.metrics import metrics_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # JSON BFF Endpoints
    path('api/gateway/home/', home, name='api_home'),
    path('api/gateway/catalogue/', catalogue_list, name='api_catalogue'),
    path('api/gateway/cart/<int:customer_id>/', cart_view, name='api_cart_view'),
    path('api/gateway/checkout/<int:customer_id>/', order_checkout, name='api_order_checkout'),
    path('api/gateway/orders/<int:order_id>/', order_detail, name='api_order_detail'),
    path('api/gateway/notifications/', notifications_api, name='api_notifications'),
    path('api/gateway/notifications/<int:customer_id>/', notifications_api, name='api_notifications_by_customer'),
    
    # Prometheus Metrics
    path('metrics/', metrics_view, name='prometheus_metrics'),
]
