import re
from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_phone(self, value):
        """Kiểm tra định dạng số điện thoại Việt Nam: 0xxxxxxxxx hoặc +84xxxxxxxxx"""
        pattern = r'^(0[0-9]{9}|\+84[0-9]{9})$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Số điện thoại không hợp lệ. Định dạng VN: 0xxxxxxxxx hoặc +84xxxxxxxxx"
            )
        return value

    def validate_email(self, value):
        if value == '':
            return None
        return value
