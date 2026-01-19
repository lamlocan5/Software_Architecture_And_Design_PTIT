from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model"""
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'stock']


class UpdateStockSerializer(serializers.Serializer):
    """Serializer for updating book stock"""
    quantity = serializers.IntegerField()
    operation = serializers.ChoiceField(choices=['reduce', 'increase'])
