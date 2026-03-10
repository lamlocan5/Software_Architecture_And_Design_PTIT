from rest_framework import serializers
from .models import Book, Publisher


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    publisher_detail = PublisherSerializer(source='publisher', read_only=True)

    class Meta:
        model = Book
        fields = '__all__'