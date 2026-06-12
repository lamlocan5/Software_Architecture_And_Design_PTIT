from django.contrib import admin
from django.urls import path
from app.views import Recommendations, BehaviorLogView, RecommendView, ChatbotView, GraphDataView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recommendations/', Recommendations.as_view()),
    path('behavior/', BehaviorLogView.as_view()),
    path('recommend/', RecommendView.as_view()),
    path('chatbot/', ChatbotView.as_view()),
    path('graph/', GraphDataView.as_view()),
]


