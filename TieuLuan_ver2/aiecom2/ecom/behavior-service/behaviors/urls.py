from django.urls import path
from .views import BehaviorView, UserSequenceView

urlpatterns = [
    path('behaviors/', BehaviorView.as_view(), name='behavior-record'),
    path('behaviors/sequence/<int:user_id>/', UserSequenceView.as_view(), name='user-sequence'),
]
