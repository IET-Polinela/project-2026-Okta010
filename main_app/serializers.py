from rest_framework import serializers
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    # Poin 3c: Override field reporter agar selalu anonim
    reporter = serializers.SerializerMethodField()

    class Meta:
        model = Report
        # Menyertakan field sesuai instruksi gambar tugasmu
        fields = ['id', 'title', 'category', 'description', 'location', 'status', 'reporter', 'created_at', 'updated_at']

    # Fungsi untuk menghasilkan string "Warga Anonim"
    def get_reporter(self, obj):
        return "Warga Anonim"