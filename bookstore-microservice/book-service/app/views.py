from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book, Publisher
from .serializers import BookSerializer, PublisherSerializer


# ── Books ─────────────────────────────────────────────────────────────────

class BookListCreate(APIView):

    def get(self, request):
        books = Book.objects.select_related('publisher').all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Publishers ────────────────────────────────────────────────────────────

class PublisherListCreate(APIView):
    """GET all publishers | POST create new publisher"""

    def get(self, request):
        publishers = Publisher.objects.all()
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublisherDetail(APIView):
    """GET / PUT / DELETE a single publisher"""

    def get_object(self, pk):
        try:
            return Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            return None

    def get(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return Response({'error': 'Không tìm thấy nhà xuất bản'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PublisherSerializer(publisher).data)

    def put(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return Response({'error': 'Không tìm thấy nhà xuất bản'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PublisherSerializer(publisher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        publisher = self.get_object(pk)
        if not publisher:
            return Response({'error': 'Không tìm thấy nhà xuất bản'}, status=status.HTTP_404_NOT_FOUND)
        publisher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
