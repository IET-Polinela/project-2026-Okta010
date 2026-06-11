from rest_framework.routers import DefaultRouter
from .api_views import ReportViewSet

# Inisialisasi DefaultRouter
router = DefaultRouter()

# Registrasi ReportViewSet ke router
# Gunakan awalan 'report' sesuai instruksi gambar
router.register(r'report', ReportViewSet, basename='report')

# Pola URL diambil otomatis dari router
urlpatterns = router.urls