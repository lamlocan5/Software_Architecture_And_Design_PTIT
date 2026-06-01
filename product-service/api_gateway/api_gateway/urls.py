from django.contrib import admin
from django.urls import path, re_path
from gateway import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # UI pages
    path('', views.home, name='home'),
    path('ui/staff/', views.staff_ui, name='staff-ui'),
    path('ui/customer/', views.customer_ui, name='customer-ui'),

    # API Proxy routes
    re_path(r'^api/customer/(?P<path>.*)$', views.customer_proxy, name='customer-proxy'),
    re_path(r'^api/staff/(?P<path>.*)$', views.staff_proxy, name='staff-proxy'),
    re_path(r'^api/laptop/(?P<path>.*)$', views.laptop_proxy, name='laptop-proxy'),
    re_path(r'^api/mobile/(?P<path>.*)$', views.mobile_proxy, name='mobile-proxy'),
    re_path(r'^api/order/(?P<path>.*)$', views.order_proxy, name='order-proxy'),
    re_path(r'^api/advisory/(?P<path>.*)$', views.advisory_proxy, name='advisory-proxy'),
]
