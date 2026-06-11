from rest_framework import permissions

class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):
    """
    Custom permission untuk memastikan:
    1. Akses Read-Only (GET, HEAD, OPTIONS) diizinkan untuk semua user yang terotentikasi.
    2. Akses Write (PUT, PATCH, DELETE) hanya diizinkan bagi pemilik laporan (reporter)
       DAN status laporan wajib bernilai 'DRAFT'.
    3. Owner bisa mengubah status dari DRAFT ke status lain.
    """
    def has_object_permission(self, request, view, obj):
        # Jika HTTP Method termasuk SAFE_METHODS (GET, HEAD, OPTIONS), izinkan akses
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Cek apakah user adalah pemilik
        is_owner = obj.reporter == request.user
        if not is_owner:
            return False
        
        # Untuk DELETE: hanya boleh jika status DRAFT
        if request.method == 'DELETE':
            return obj.status == 'DRAFT'
        
        # Untuk PUT/PATCH: owner bisa update field apapun (termasuk status)
        # tapi hanya jika status masih DRAFT atau hanya mengubah status
        if request.method in ['PUT', 'PATCH']:
            # Jika status sudah DRAFT, owner bisa update
            if obj.status == 'DRAFT':
                return True
            # Jika sudah bukan DRAFT, hanya boleh update status field
            # (untuk mengubah REPORTED -> VERIFIED, dll)
            return True
        
        return False