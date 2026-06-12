from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from app.views import (
    MyTokenObtainPairView, MeView, CustomerListCreate,
    StaffListCreate, StaffDetail, ManagerListCreate, ManagerDetail,
    VerifyUserCredentials, AuthVerifyView
)
from app.metrics import metrics_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Token & Me
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/me/', MeView.as_view(), name='me'),

    # Customers
    path('customers/', CustomerListCreate.as_view()),

    # Staff
    path('staff/', StaffListCreate.as_view()),
    path('staff/<int:pk>/', StaffDetail.as_view()),

    # Managers
    path('managers/', ManagerListCreate.as_view()),
    path('managers/<int:pk>/', ManagerDetail.as_view()),

    # Verification (Helper for session gateway auth)
    path('users/verify/', VerifyUserCredentials.as_view()),
    path('api/auth/verify/', AuthVerifyView.as_view(), name='auth_verify'),

    # Prometheus Metrics
    path('metrics/', metrics_view, name='prometheus_metrics'),
]

