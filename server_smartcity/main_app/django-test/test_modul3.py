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
# MODUL 3: PENGUJIAN ALUR KERJA & ATURAN BISNIS STATUS LAPORAN
# =============================================================================
# Fokus: Memastikan transisi status laporan mengikuti aturan state machine:
#   DRAFT -> REPORTED -> VERIFIED -> IN_PROGRESS -> RESOLVED
#
# Aturan kunci:
#   - Hanya pemilik draf yang bisa memodifikasi laporan berstatus DRAFT
#   - Laporan yang sudah REPORTED tidak bisa diubah kontennya oleh warga
#   - Laporan RESOLVED bersifat read-only (tidak bisa diubah siapa pun)
#   - Admin hanya bisa melakukan transisi maju, BUKAN lompat status
# =============================================================================

class WorkflowStateTests(APITestCase):
    """
    Kelas pengujian untuk alur kerja dan transisi status laporan via REST API.

    Menguji aturan bisnis terkait kapan laporan boleh dimodifikasi dan
    bagaimana status berubah sesuai alur yang telah ditentukan.
    """

    def setUp(self):
        """
        Persiapan: Buat satu warga dan beberapa laporan dengan status berbeda
        untuk menguji aturan transisi status.
        """
        self.warga = User.objects.create_user(
            username='warga_wf', password='TestPass123!', is_admin=False
        )

        # Laporan berstatus DRAFT — bisa dimodifikasi oleh pemilik
        self.laporan_draft = Report.objects.create(
            title='Lampu Kampus Mati',
            category='Fasilitas Umum',
            description='Lampu di depan gedung rektorat tidak menyala.',
            location='Gedung Rektorat',
            status='DRAFT',
            reporter=self.warga,
        )

        # Laporan berstatus REPORTED — sudah masuk antrean, TIDAK bisa diubah
        self.laporan_reported = Report.objects.create(
            title='Saluran Air Tersumbat',
            category='Infrastruktur',
            description='Saluran air di samping kantin tersumbat.',
            location='Kantin Polinela',
            status='REPORTED',
            reporter=self.warga,
        )

        # Laporan berstatus RESOLVED — sudah selesai, bersifat READ-ONLY
        self.laporan_resolved = Report.objects.create(
            title='AC Rusak di Lab',
            category='Fasilitas Umum',
            description='AC di Lab CPS 1 sudah diperbaiki.',
            location='Lab CPS 1',
            status='RESOLVED',
            reporter=self.warga,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-01: Warga Mengajukan Laporan (DRAFT → REPORTED)
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_01_warga_mengajukan_draf_menjadi_reported(self):
        """
        [WF-01] Warga menekan tombol ajukan laporan pada data berstatus DRAFT.

        SKENARIO:
            Warga melakukan PUT request untuk mengubah status laporan dari
            DRAFT menjadi REPORTED. Ini mensimulasikan aksi "Ajukan Laporan"
            pada antarmuka SPA.

        HASIL YANG DIHARAPKAN:
            Status laporan di basis data berubah menjadi REPORTED dan laporan
            masuk ke antrean peninjauan petugas.

        PENJELASAN TEKNIS:
            Pada kode SPA (app.js), fungsi kirimLaporan() mengirim PUT request
            dengan payload yang menyertakan status='REPORTED'. Permission
            IsOwnerAndDraftOrReadOnly mengizinkan modifikasi karena user adalah
            pemilik dan status saat ini masih DRAFT.
        """
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_draft.pk}/'
        payload = {
            'title': self.laporan_draft.title,
            'category': self.laporan_draft.category,
            'description': self.laporan_draft.description,
            'location': self.laporan_draft.location,
            'status': 'REPORTED',  # Modifikasi dari DRAFT ke REPORTED
        }

        response = self.client.put(url, payload, format='json')

        # Verifikasi: PUT berhasil dengan HTTP 200
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Pengajuan draf ke REPORTED seharusnya berhasil (HTTP 200)"
        )

        # Verifikasi: Status di database benar-benar berubah
        self.laporan_draft.refresh_from_db()
        self.assertEqual(
            self.laporan_draft.status,
            'REPORTED',
            "Status laporan di database harus berubah menjadi 'REPORTED'"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-02: Warga Tidak Bisa Mengubah Konten Laporan yang Sudah REPORTED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_02_tidak_bisa_edit_laporan_yang_sudah_reported(self):
        """
        [WF-02] Warga mencoba memperbarui teks konten laporan yang sudah
        berstatus REPORTED via API.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_reported.pk}/'

        payload = {
            'title': 'Judul Baru',
            'category': self.laporan_reported.category,
            'description': 'Deskripsi telah diubah.',
            'location': self.laporan_reported.location,
            'status': 'REPORTED',
        }

        # Act
        response = self.client.put(
            url,
            payload,
            format='json'
        )

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan yang sudah REPORTED tidak boleh diubah."
        )

        # Pastikan data di database tidak berubah
        self.laporan_reported.refresh_from_db()

        self.assertEqual(
            self.laporan_reported.title,
            "Saluran Air Tersumbat"
        )

        self.assertEqual(
            self.laporan_reported.description,
            "Saluran air di samping kantin tersumbat."
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-05: Laporan RESOLVED Bersifat Read-Only
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_05_laporan_resolved_tidak_bisa_diubah(self):
        """
        [WF-05] Pengguna (Admin maupun Warga) mencoba mengirimkan modifikasi
        data pada laporan yang sudah berstatus RESOLVED.
        """

        # Arrange
        self.client.force_authenticate(user=self.warga)

        url = f'/api/report/{self.laporan_resolved.pk}/'

        payload = {
            'title': 'Judul Diubah',
            'category': self.laporan_resolved.category,
            'description': 'Deskripsi telah diubah.',
            'location': self.laporan_resolved.location,
            'status': 'RESOLVED',
        }

        # Act
        response = self.client.put(
            url,
            payload,
            format='json'
        )

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Laporan yang sudah RESOLVED harus bersifat read-only."
        )

        # Pastikan data di database tidak berubah
        self.laporan_resolved.refresh_from_db()

        self.assertEqual(
            self.laporan_resolved.title,
            "AC Rusak di Lab"
        )

        self.assertEqual(
            self.laporan_resolved.description,
            "AC di Lab CPS 1 sudah diperbaiki."
        )

# =============================================================================
# MODUL 3b: PENGUJIAN ADMIN PORTAL — TRANSISI STATUS
# =============================================================================
# Fokus: Menguji fungsi portal admin (Django monolitik) dalam mengelola
# transisi status laporan dan memastikan tombol aksi yang tersedia sesuai
# dengan aturan state machine.
#
# Catatan: Menggunakan Django TestCase (bukan APITestCase) karena menguji
# Django Views + Templates (monolitik), bukan REST API.
# =============================================================================

class AdminWorkflowTests(TestCase):
    """
    Kelas pengujian untuk portal admin (Django monolithic views).

    Menguji kemampuan admin untuk mengubah status laporan melalui
    antarmuka portal admin, serta memverifikasi pembatasan transisi status.
    """

    def setUp(self):
        """
        Persiapan: Buat admin user dan beberapa laporan untuk menguji
        transisi status di portal admin.
        """
        # Admin harus memiliki is_staff=True untuk lolos @staff_member_required
        self.admin = User.objects.create_user(
            username='admin_portal',
            password='AdminPass123!',
            is_admin=True,
            is_staff=True,
        )

        # Laporan REPORTED — menunggu verifikasi oleh admin
        self.laporan_reported = Report.objects.create(
            title='Jalan Rusak di Blok C',
            category='Infrastruktur',
            description='Jalan berlubang parah di area parkir Blok C.',
            location='Blok C Polinela',
            status='REPORTED',
            reporter=self.admin,  # Siapa reporter-nya tidak penting untuk admin test
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-03: Admin Mengubah Status REPORTED menjadi VERIFIED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_03_admin_mengubah_status_reported_ke_verified(self):
        # Arrange
        self.client.login(
            username='admin_portal',
            password='AdminPass123!'
        )

        # Act
        response = self.client.post(
            reverse('update_status', args=[self.laporan_reported.id]),
            {
                'status': 'VERIFIED'
            },
            follow=True
        )

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.laporan_reported.refresh_from_db()

        self.assertEqual(
            self.laporan_reported.status,
            'VERIFIED'
        )

    # ─────────────────────────────────────────────────────────────────────────
    # WF-04: Tidak Ada Tombol Langsung ke RESOLVED dari REPORTED
    # ─────────────────────────────────────────────────────────────────────────
    def test_WF_04_tidak_ada_transisi_langsung_ke_resolved_dari_reported(self):
        # Arrange
        self.client.login(
            username="admin_portal",
            password="AdminPass123!"
        )

        # Act
        response = self.client.get(
            reverse("report_detail", args=[self.laporan_reported.id])
        )

        # Assert
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "VERIFIED")

        self.assertNotContains(response, "RESOLVED")