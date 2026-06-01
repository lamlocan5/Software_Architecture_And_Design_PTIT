from rest_framework import serializers
from .models import Bill, BillItem


class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = ['id', 'description', 'unit_price', 'quantity']


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)

    class Meta:
        model = Bill
        fields = ['id', 'patient_id', 'prescription_id', 'total_amount', 'status', 'items', 'created_at', 'paid_at']
        read_only_fields = ['id', 'total_amount', 'status', 'created_at', 'paid_at']


class CreateBillInternalSerializer(serializers.Serializer):
    """Serializer cho internal endpoint từ clinical-service."""
    patient_id = serializers.IntegerField()
    prescription_id = serializers.IntegerField(required=False, allow_null=True)
    items = serializers.ListField(
        child=serializers.DictField(), min_length=1
    )

    def validate_items(self, value):
        for item in value:
            if 'description' not in item:
                raise serializers.ValidationError("Mỗi item phải có 'description'.")
            if 'quantity' not in item:
                raise serializers.ValidationError("Mỗi item phải có 'quantity'.")
        return value
