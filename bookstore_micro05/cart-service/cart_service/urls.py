"""
URL configuration for cart_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from app.views import CartCreate, AddCartItem, ViewCart

urlpatterns = [
    path("admin/", admin.site.urls),
    path("carts/", CartCreate.as_view(), name="cart_create"),
    path("carts/add-item/", AddCartItem.as_view(), name="add_cart_item"),
    path("carts/<int:customer_id>/", ViewCart.as_view(), name="view_cart"),
    path("", RedirectView.as_view(url="/carts/", permanent=False)),
]

