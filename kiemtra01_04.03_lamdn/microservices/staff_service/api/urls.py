from django.urls import path
from .views import info, register_staff, login_staff, get_profile, update_profile
urlpatterns=[path("info/",info),path("register/",register_staff),path("login/",login_staff),path("profile/",get_profile),path("profile/update/",update_profile)]
