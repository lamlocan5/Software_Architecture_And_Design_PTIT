from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count
from .models import Review
from .serializers import ReviewSerializer


class ReviewList(APIView):
    """GET tất cả đánh giá | POST thêm đánh giá mới"""

    def get(self, request):
        reviews = Review.objects.all().order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookReviews(APIView):
    """GET tất cả đánh giá cho 1 cuốn sách"""

    def get(self, request, book_id):
        reviews = Review.objects.filter(book_id=book_id).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewStats(APIView):
    """GET thống kê đánh giá cho 1 cuốn sách (avg rating, count)"""

    def get(self, request, book_id):
        stats = Review.objects.filter(book_id=book_id).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
        )
        stats['book_id'] = book_id
        stats['avg_rating'] = round(stats['avg_rating'] or 0, 1)
        return Response(stats)
