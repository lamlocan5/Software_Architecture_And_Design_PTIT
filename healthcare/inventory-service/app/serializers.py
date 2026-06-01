from rest_framework import serializers
from .models import Medicine, StockTransaction


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'
        read_only_fields = ['id', 'updated_at']

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Tồn kho không được âm.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Đơn giá phải lớn hơn 0.")
        return value


class StockUpdateSerializer(serializers.Serializer):
    """Serializer cho PATCH /medicines/{id}/stock/"""
    quantity = serializers.IntegerField()
    transaction_type = serializers.ChoiceField(choices=['import', 'export'])
    reference_id = serializers.CharField(required=False, allow_blank=True)


class StockTransactionSerializer(serializers.ModelSerializer):
    medicine_name = serializers.CharField(source='medicine.name', read_only=True)

    class Meta:
        model = StockTransaction
        fields = ['id', 'medicine', 'medicine_name', 'transaction_type', 'quantity', 'reference_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class DeductStockInternalSerializer(serializers.Serializer):
    """Serializer cho internal endpoint /internal/deduct-stock/"""
    prescription_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField(), min_length=1
    )

    def validate_items(self, value):
        for item in value:
            if 'medicine_name' not in item:
                raise serializers.ValidationError("Mỗi item phải có 'medicine_name'.")
            if 'quantity' not in item or int(item['quantity']) <= 0:
                raise serializers.ValidationError("Mỗi item phải có 'quantity' > 0.")
        return value
