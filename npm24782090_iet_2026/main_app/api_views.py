from rest_framework import viewsets, permissions
from .models import Report
from .serializers import ReportSerializer
from .permissions import IsOwnerAndDraftOrReadOnly

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def get_permissions(self):
        """
        Menentukan aturan hak akses secara dinamis berdasarkan aksi HTTP.
        """
        # Aksi edit (update/partial_update) & hapus (destroy) wajib lolos cek kepemilikan & status DRAFT
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerAndDraftOrReadOnly()]
            
        # Aksi list, detail, dan create secara umum wajib login terlebih dahulu
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Otomatis mengasosiasikan field 'reporter' dengan user yang sedang login
        saat membuat data laporan baru melalui API.
        """
        serializer.save(reporter=self.request.user)
        