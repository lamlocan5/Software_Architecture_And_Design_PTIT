from rest_framework import serializers
from .models import Appointment, Prescription, PrescriptionItem


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = ['id', 'medicine_name', 'quantity', 'dosage']


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True)

    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'patient_id', 'diagnosis', 'items', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Đơn thuốc phải có ít nhất 1 thuốc.")
        for item in value:
            if item.get('quantity', 0) <= 0:
                raise serializers.ValidationError(
                    f"Số lượng thuốc '{item.get('medicine_name')}' phải lớn hơn 0."
                )
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)
        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)
        return prescription
