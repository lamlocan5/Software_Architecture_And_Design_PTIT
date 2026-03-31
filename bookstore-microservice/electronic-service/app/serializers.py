from rest_framework import serializers
from .models import Electronic, ElectronicCategory


class ElectronicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicCategory
        fields = '__all__'


class ElectronicSerializer(serializers.ModelSerializer):
    category_detail = ElectronicCategorySerializer(source='category', read_only=True)

    class Meta:
        model = Electronic
        fields = '__all__'

