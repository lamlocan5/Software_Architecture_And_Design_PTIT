from django.contrib import admin
from django.urls import path
from app.views import ReviewList, BookReviews, ReviewStats

urlpatterns = [
    path('admin/', admin.site.urls),

    path('reviews/', ReviewList.as_view()),
    path('reviews/book/<int:book_id>/', BookReviews.as_view()),
    path('reviews/stats/<int:book_id>/', ReviewStats.as_view()),
]
