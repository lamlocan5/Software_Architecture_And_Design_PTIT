from django.contrib import admin
from django.urls import path
from api_gateway.views import (
    home,
    book_list, book_detail, book_edit,
    catalogue_list,
    staff_list,
    manager_list,
    customer_list, cart_view,
    order_list, order_checkout, order_detail,
    review_list, publisher_list,
    payment_list, shipment_list,
    publisher_edit,
    clothes_list,
    clothe_detail,
    electronics_list,
    electronic_detail,
    notification_list,
)
from api_gateway.auth_views import login_view, logout_view, register_view

from api_gateway.metrics import metrics_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),
    path('register/', register_view, name='register'),

    # Pages
    path('',                               home,           name='home'),
    path('catalogue/',                     catalogue_list, name='catalogue_list'),
    path('books/',                         book_list,      name='book_list'),
    path('books/<int:book_id>/',           book_detail,    name='book_detail'),
    path('books/<int:book_id>/edit/',       book_edit,      name='book_edit'),
    path('staff/',                         staff_list,     name='staff_list'),
    path('managers/',                      manager_list,   name='manager_list'),
    path('customers/',                     customer_list,  name='customer_list'),
    path('cart/<int:customer_id>/',        cart_view,      name='cart_view'),
    path('orders/',                        order_list,     name='order_list'),
    path('orders/<int:order_id>/',         order_detail,   name='order_detail'),
    path('orders/checkout/<int:customer_id>/', order_checkout, name='order_checkout'),
    path('payments/',                      payment_list,   name='payment_list'),
    path('shipments/',                     shipment_list,  name='shipment_list'),
    path('reviews/',                       review_list,    name='review_list'),
    path('publishers/',                    publisher_list, name='publisher_list'),
    path('publishers/<int:publisher_id>/edit/', publisher_edit, name='publisher_edit'),
    path('clothes/',                       clothes_list,   name='clothes_list'),
    path('clothes/<int:clothe_id>/',       clothe_detail,  name='clothe_detail'),
    path('electronics/',                   electronics_list,   name='electronics_list'),
    path('electronics/<int:electronic_id>/', electronic_detail,  name='electronic_detail'),
    path('notifications/',                 notification_list,  name='notification_list'),

    # Prometheus Metrics
    path('metrics/', metrics_view, name='prometheus_metrics'),
]
