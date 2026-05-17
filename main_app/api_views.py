from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer

class ReportViewSet(viewsets.ModelViewSet):
    # Mengizinkan akses siapa saja ke API ini
    permission_classes = [permissions.AllowAny]
    # Mengambil semua data dari model Report
    queryset = Report.objects.all()
    # Menggunakan serializer yang baru saja kita buat
    serializer_class = ReportSerializer