import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


BOOK_SERVICE_URL = "http://product-service:8000"
REVIEW_SERVICE_URL = "http://review-service:8000"


def _get(url, default=None):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code >= 400:
            return default if default is not None else []
        return r.json()
    except Exception:
        return default if default is not None else []


class CatalogueBookList(APIView):
    """
    GET /catalog/books/
    Trả về danh sách sách đã ghép thêm thống kê review (avg_rating, total_reviews).
    """

    def get(self, request):
        books = _get(f"{BOOK_SERVICE_URL}/books/", [])
        if not isinstance(books, list):
            return Response(
                {"detail": "Upstream book-service error"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        for book in books:
            book_id = book.get("id")
            if not book_id:
                continue
            stats = _get(f"{REVIEW_SERVICE_URL}/reviews/stats/{book_id}/", {})
            if isinstance(stats, dict):
                book["avg_rating"] = stats.get("avg_rating", 0)
                book["total_reviews"] = stats.get("total_reviews", 0)

        return Response(books)


class CatalogueBookDetail(APIView):
    """
    GET /catalog/books/<id>/
    Trả về chi tiết 1 sách + thống kê review.
    """

    def get(self, request, pk):
        books = _get(f"{BOOK_SERVICE_URL}/books/", [])
        if not isinstance(books, list):
            return Response(
                {"detail": "Upstream book-service error"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        book = next((b for b in books if b.get("id") == pk), None)
        if not book:
            return Response(
                {"detail": "Book not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        stats = _get(f"{REVIEW_SERVICE_URL}/reviews/stats/{pk}/", {})
        if isinstance(stats, dict):
            book["avg_rating"] = stats.get("avg_rating", 0)
            book["total_reviews"] = stats.get("total_reviews", 0)

        return Response(book)


