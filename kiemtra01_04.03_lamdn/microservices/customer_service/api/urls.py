from django.urls import path
from .views import info, register, login, search, create_cart, add_item, update_item, delete_item, checkout, get_profile, update_profile
urlpatterns=[path("info/",info),path("register/",register),path("login/",login),path("search/",search),path("carts/",create_cart),path("carts/items/",add_item),path("carts/items/<int:item_id>/",update_item),path("carts/items/<int:item_id>/delete/",delete_item),path("carts/checkout/",checkout),path("profile/",get_profile),path("profile/update/",update_profile)]
