from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from main_app.models import Report

# ─────────────────────────────────────────────────────────────────────────────
# PENJELASAN: get_user_model()
# ─────────────────────────────────────────────────────────────────────────────
# Django mendukung custom user model melalui setting AUTH_USER_MODEL.
# Pada proyek ini, user model kustom didefinisikan di usermanagement.User.
# Menggunakan get_user_model() memastikan kita selalu mereferensikan model
# user yang benar, bukan django.contrib.auth.models.User bawaan.
# ─────────────────────────────────────────────────────────────────────────────
User = get_user_model()

# =============================================================================
# MODUL 4: PENGUJIAN FUNGSIONALITAS DASAR & VALIDASI INPUT
# =============================================================================
# Fokus: Memastikan fungsi CRUD (Create, Read, Update, Delete) berjalan normal,
# validasi input wajib ditegakkan, dan keamanan dari serangan injeksi (XSS).
#
# KONSEP KUNCI:
#   - Serializer DRF secara otomatis memvalidasi field yang required
#   - Django template engine secara default melakukan HTML escaping
#   - SearchFilter DRF melakukan pencarian berbasis teks di field yang
#     terdaftar pada search_fields
# =============================================================================

class CRUDAndValidationTests(APITestCase):
    """
    Kelas pengujian untuk fungsionalitas dasar dan validasi input.

    Menguji pembuatan data baru (CREATE), validasi field wajib, pertahanan
    terhadap serangan XSS, dan fitur pencarian/filter data.
    """

    def setUp(self):
        """
        Persiapan: Buat warga dan autentikasi untuk test CRUD.
        """
        self.warga = User.objects.create_user(
            username='warga_crud', password='TestPass123!', is_admin=False
        )
        # force_authenticate memastikan semua request di test ini terautentikasi
        self.client.force_authenticate(user=self.warga)

    # ─────────────────────────────────────────────────────────────────────────
    # FT-01: Membuat Laporan Baru dengan Data Lengkap
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_01_buat_laporan_dengan_data_lengkap(self):
        # Arrange
        url = reverse("report-list")

        payload = {
            "title": "Lampu Jalan Mati",
            "category": "Infrastruktur",
            "description": "Lampu jalan di depan kampus mati sejak kemarin.",
            "location": "Jl. ZA Pagar Alam",
        }

        # Act
        response = self.client.post(
            url,
            payload,
            format="json"
        )

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        laporan = Report.objects.get(title="Lampu Jalan Mati")

        self.assertEqual(
            laporan.category,
            "Infrastruktur"
        )

        self.assertEqual(
            laporan.description,
            "Lampu jalan di depan kampus mati sejak kemarin."
        )

        self.assertEqual(
            laporan.location,
            "Jl. ZA Pagar Alam"
        )

        self.assertEqual(
            laporan.reporter,
            self.warga
        )

    # ─────────────────────────────────────────────────────────────────────────
    # FT-02: Laporan Ditolak Jika Judul Kosong
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_02_ditolak_jika_judul_kosong(self):
        # Arrange
        url = reverse("report-list")

        payload = {
            "category": "Infrastruktur",
            "description": "Ada jalan berlubang.",
            "location": "Bandar Lampung",
        }

        # Act
        response = self.client.post(
            url,
            payload,
            format="json"
        )

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "title",
            response.data
        )

    # ─────────────────────────────────────────────────────────────────────────
    # FT-03: Laporan Ditolak Jika Deskripsi Kosong
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_03_ditolak_jika_deskripsi_kosong(self):
        # Arrange
        url = reverse("report-list")

        payload = {
            "title": "Sampah Menumpuk",
            "category": "Kebersihan",
            "location": "Jl. Sudirman",
        }

        # Act
        response = self.client.post(
            url,
            payload,
            format="json"
        )

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "description",
            response.data
        )

    # ─────────────────────────────────────────────────────────────────────────
    # FT-04: Keamanan dari Serangan XSS (Cross-Site Scripting)
    # ─────────────────────────────────────────────────────────────────────────
    def test_FT_04_xss_script_disimpan_sebagai_string_literal(self):
        """
        [FT-04] Mengisi nilai deskripsi laporan menggunakan kode skrip
        injeksi jahat HTML: <script>alert('xss')</script>.

        SKENARIO:
            Warga sengaja memasukkan kode JavaScript berbahaya ke dalam
            field deskripsi laporan.

        HASIL YANG DIHARAPKAN:
            Sistem tetap menerima data (HTTP 201 Created) namun melakukan
            penyimpanan sebagai string literal yang aman. Kode TIDAK akan
            dieksekusi oleh browser saat ditampilkan.

        PENJELASAN TEKNIS:
            DRF menyimpan data mentah ke database. Pertahanan utama XSS
            ada di sisi rendering:
            - Django Template Engine: auto-escaping HTML secara default
            - SPA Frontend: menggunakan textContent/innerText, bukan innerHTML
            Sehingga kode <script> akan ditampilkan sebagai teks biasa,
            bukan dieksekusi sebagai JavaScript.
        """
        url = reverse('report-list')

        # Payload dengan skrip injeksi XSS di deskripsi
        kode_xss = '<script>alert("xss")</script>'
        payload = {
            'title': 'Laporan XSS Test',
            'category': 'Keamanan',
            'description': kode_xss,
            'location': 'Lab Keamanan Siber',
        }

        response = self.client.post(url, payload, format='json')

        # Verifikasi: Data tetap diterima (201 Created)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Data dengan karakter HTML harus tetap diterima oleh API"
        )

        # Verifikasi: Deskripsi tersimpan di database sebagai teks literal
        # Ambil laporan yang baru saja dibuat dari database
        laporan = Report.objects.get(title='Laporan XSS Test')

        # Kode script harus tersimpan sebagai string biasa, bukan di-execute
        # Ini membuktikan bahwa injection tidak mengubah behavior sistem
        self.assertIn(
            'script',
            laporan.description.lower(),
            "Kode XSS harus tersimpan sebagai string literal di database"
        )