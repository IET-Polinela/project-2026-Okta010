from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    # Buat field reporter menjadi CharField Read-Only agar mau menerima 
    # objek user langsung dari view tanpa validasi ketat
    reporter = serializers.CharField(read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'title', 'category', 'description', 'location', 'status', 'reporter', 'created_at', 'updated_at']

    # Trik merubah nama ID user asli menjadi "Warga Anonim" saat dikirim kembali ke Postman
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['reporter'] = "Warga Anonim"
        return representation