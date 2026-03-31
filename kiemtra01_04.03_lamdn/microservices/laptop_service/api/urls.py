from django.urls import path
from .views import info, list_products, create_product, delete_product, update_product
urlpatterns=[path("info/",info),path("products/",list_products),path("products/create/",create_product),path("products/<int:id>/delete/",delete_product),path("products/<int:id>/update/",update_product)]
