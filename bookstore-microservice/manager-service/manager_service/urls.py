from django.contrib import admin
from django.urls import path
from app.views import ManagerListCreate, ManagerDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('managers/', ManagerListCreate.as_view()),
    path('managers/<int:pk>/', ManagerDetail.as_view()),
]

