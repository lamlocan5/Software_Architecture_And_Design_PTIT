from django.urls import path, include

urlpatterns = [
    path('advisor/', include('api.urls')),
]
