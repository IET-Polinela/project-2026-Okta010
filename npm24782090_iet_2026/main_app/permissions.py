from rest_framework import permissions

class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):
    """
    Custom permission untuk memastikan:
    1. Akses Read-Only (GET, HEAD, OPTIONS) diizinkan untuk semua user yang terotentikasi.
    2. Akses Write (PUT, PATCH, DELETE) hanya diizinkan bagi pemilik laporan (reporter)
       DAN status laporan wajib bernilai 'DRAFT'.
    """
    def has_object_permission(self, request, view, obj):
        # Jika HTTP Method termasuk SAFE_METHODS (GET, HEAD, OPTIONS), izinkan akses
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Untuk PUT, PATCH, DELETE: Cek apakah user adalah pemilik DAN statusnya masih DRAFT
        return obj.reporter == request.user and obj.status == 'DRAFT'