from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'title', 'category', 'description', 'location', 'status', 'reporter', 'is_owner', 'created_at', 'updated_at']

    def get_reporter(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.reporter == request.user:
            return obj.reporter.username
        return "Warga Anonim"

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return bool(request and request.user.is_authenticated and obj.reporter == request.user)

    def validate_status(self, value):
        """
        Validasi alur perubahan status laporan:
        - DRAFT dapat berubah ke REPORTED
        - REPORTED dapat berubah ke VERIFIED, IN_PROGRESS, atau kembali ke DRAFT
        - VERIFIED dapat berubah ke IN_PROGRESS
        - IN_PROGRESS dapat berubah ke RESOLVED
        - RESOLVED adalah status final
        """
        instance = self.instance
        if instance is None:
            # Ketika membuat baru, status default adalah DRAFT
            return value
        
        current_status = instance.status
        allowed_transitions = {
            'DRAFT': ['REPORTED', 'DRAFT'],
            'REPORTED': ['VERIFIED', 'IN_PROGRESS', 'DRAFT'],
            'VERIFIED': ['IN_PROGRESS', 'REPORTED'],
            'IN_PROGRESS': ['RESOLVED', 'REPORTED'],
            'RESOLVED': ['RESOLVED'],
        }
        
        if current_status in allowed_transitions:
            if value not in allowed_transitions[current_status]:
                raise serializers.ValidationError(
                    f"Tidak bisa mengubah status dari {current_status} ke {value}. "
                    f"Status yang diperbolehkan: {', '.join(allowed_transitions[current_status])}"
                )
        
        return value