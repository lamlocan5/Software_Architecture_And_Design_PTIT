from django.contrib import admin
from django.urls import path
from app.views import Recommendations

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recommendations/', Recommendations.as_view()),
]

