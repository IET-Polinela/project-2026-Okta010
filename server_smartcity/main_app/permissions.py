from rest_framework import permissions


class IsOwnerAndDraftOrReadOnly(permissions.BasePermission):
    """
    Hanya pemilik laporan yang boleh mengubah data,
    dan hanya jika status laporan masih DRAFT.
    """

    def has_object_permission(self, request, view, obj):

        # GET / HEAD / OPTIONS selalu boleh
        if request.method in permissions.SAFE_METHODS:
            return True

        # Harus pemilik laporan
        if obj.reporter != request.user:
            return False

        # PUT, PATCH, DELETE hanya boleh saat DRAFT
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return obj.status == "DRAFT"

        return False