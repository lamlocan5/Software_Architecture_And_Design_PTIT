from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("orders/", include("orders.urls")),
    path("payments/", include("payments.urls")),
    path("", include("catalog.urls")),
    path("users/", include("users.urls")),
    path("cart/", include("cart.urls")),
]
