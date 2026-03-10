from django.contrib import admin
from django.urls import path
from app.views import StaffListCreate, StaffDetail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('staff/', StaffListCreate.as_view()),
    path('staff/<int:pk>/', StaffDetail.as_view()),
]

