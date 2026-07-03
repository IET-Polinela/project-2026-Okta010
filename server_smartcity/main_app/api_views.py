from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied

from .models import Report
from .serializers import ReportSerializer
from .permissions import IsOwnerAndDraftOrReadOnly

class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().order_by('-updated_at')
    serializer_class = ReportSerializer
    pagination_class = ReportPagination

    def get_queryset(self):
        queryset = Report.objects.all().order_by('-updated_at')
        user = self.request.user
        tab = self.request.query_params.get('tab')

        if tab == 'my_reports':
            return queryset.filter(reporter=user)

        if tab == 'feed':
            return queryset.exclude(status='DRAFT').exclude(reporter=user)

        # Untuk detail/update/delete:
        # tampilkan semua laporan publik + draft milik sendiri
        return queryset.exclude(
            status='DRAFT'
        ) | queryset.filter(
            reporter=user
        )

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
        Citizen boleh membuat laporan.
        Admin tidak diperbolehkan membuat laporan melalui SPA.
        """

        if self.request.user.is_staff:
            raise PermissionDenied(
                "Admin tidak diperbolehkan membuat laporan."
            )

        serializer.save(reporter=self.request.user)