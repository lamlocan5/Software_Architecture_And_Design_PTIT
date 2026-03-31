from django.urls import path, re_path

from .views import gateway_health, proxy_to_customer, proxy_to_laptop, proxy_to_moblie, proxy_to_staff

urlpatterns = [
    path("health/", gateway_health),
    re_path(r"^api/staff/(?P<upstream_path>.*)$", proxy_to_staff),
    re_path(r"^api/customer/(?P<upstream_path>.*)$", proxy_to_customer),
    re_path(r"^api/laptop/(?P<upstream_path>.*)$", proxy_to_laptop),
    re_path(r"^api/moblie/(?P<upstream_path>.*)$", proxy_to_moblie),
]
