// js/app.js
console.log("Bandung City Citizen SPA (NPM: 24782090) Berhasil Dimuat.");

let currentTab = 'my_reports';
let currentPage = 1;
let editingReportId = null;
let reportModal = null;

function statusBadgeClass(status) {
    switch (status) {
        case 'DRAFT':
            return 'bg-warning text-dark';
        case 'REPORTED':
            return 'bg-info text-dark';
        case 'VERIFIED':
            return 'bg-primary';
        case 'IN_PROGRESS':
            return 'bg-secondary';
        case 'RESOLVED':
            return 'bg-success';
        default:
            return 'bg-light text-dark';
    }
}

function statusProgress(status) {
    switch (status) {
        case 'DRAFT':
            return { value: 15, label: 'Draft', barClass: 'bg-warning' };
        case 'REPORTED':
            return { value: 40, label: 'Dilaporkan', barClass: 'bg-info' };
        case 'VERIFIED':
            return { value: 60, label: 'Terverifikasi', barClass: 'bg-primary' };
        case 'IN_PROGRESS':
            return { value: 80, label: 'Sedang Diproses', barClass: 'bg-secondary' };
        case 'RESOLVED':
            return { value: 100, label: 'Selesai', barClass: 'bg-success' };
        default:
            return { value: 0, label: 'Unknown', barClass: 'bg-light' };
    }
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('id-ID', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// loadDashboardData: fetch paginated report data from the API and update the UI
// by rendering the report cards and pagination controls.
async function setupDashboard() {
    const dashboardTabs = document.getElementById('dashboardTabs');
    if (dashboardTabs) {
        dashboardTabs.innerHTML = [
            { key: 'my_reports', label: 'Laporan Saya' },
            { key: 'feed', label: 'Feed Kota' }
        ].map(tab => `
            <button type="button" class="nav-link ${tab.key === currentTab ? 'active' : ''}" data-tab="${tab.key}">
                ${tab.label}
            </button>
        `).join('');

        dashboardTabs.querySelectorAll('button[data-tab]').forEach(button => {
            button.addEventListener('click', function () {
                currentTab = this.dataset.tab;
                currentPage = 1;
                dashboardTabs.querySelectorAll('button').forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                loadDashboardData(currentTab, currentPage);
            });
        });
    }

    const openButton = document.getElementById('openReportModalBtn');
    const logoutButton = document.getElementById('logoutBtn');
    const saveDraftButton = document.getElementById('saveDraftBtn');
    const submitReportButton = document.getElementById('submitReportBtn');

    const modalElement = document.getElementById('reportModal');
    if (modalElement) {
        reportModal = new bootstrap.Modal(modalElement);
    }

    openButton?.addEventListener('click', () => {
        openReportModal();
    });

    logoutButton?.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.hash = '#login';
    });

    saveDraftButton?.addEventListener('click', () => submitReport('DRAFT'));
    submitReportButton?.addEventListener('click', () => submitReport('REPORTED'));

    await loadDashboardData(currentTab, currentPage);
}

// Ambil daftar laporan terpaginated lalu perbarui UI dengan renderList dan renderPagination.
async function loadDashboardData(tab = 'my_reports', page = 1) {
    currentTab = tab;
    currentPage = page;

    const reportList = document.getElementById('reportList');
    const paginationNav = document.getElementById('paginationNav');

    if (reportList) {
        reportList.innerHTML = '<div class="text-center py-5 text-muted">Memuat data laporan...</div>';
    }

    try {
        const response = await requestAPI(`/api/report/?tab=${tab}&page=${page}`);

        if (response.status === 401) {
            alert('Token tidak valid. Silakan login ulang.');
            localStorage.removeItem('access_token');
            window.location.hash = '#login';
            return;
        }

        const data = await response.json();
        const reports = data.results || [];

        renderList(reports, tab);
        renderPagination(data, tab);
        await loadSummaryStats();
    } catch (error) {
        if (reportList) {
            reportList.innerHTML = '<div class="alert alert-danger">Gagal memuat laporan. Cek koneksi backend.</div>';
        }
        console.error('loadDashboardData error:', error);
    }
}

async function loadSummaryStats() {
    try {
        const response = await requestAPI('/api/report/?tab=my_reports&page_size=1000');
        const data = await response.json();
        const reports = data.results || [];

        const draftCount = reports.filter(item => item.status === 'DRAFT').length;
        const inProgressCount = reports.filter(item => ['REPORTED', 'VERIFIED', 'IN_PROGRESS'].includes(item.status)).length;
        const resolvedCount = reports.filter(item => item.status === 'RESOLVED').length;

        document.getElementById('summaryDraft').textContent = draftCount;
        document.getElementById('summaryInProgress').textContent = inProgressCount;
        document.getElementById('summaryResolved').textContent = resolvedCount;
    } catch (error) {
        console.error('loadSummaryStats error:', error);
    }
}

function renderList(reports, tab) {
    const reportList = document.getElementById('reportList');
    if (!reportList) return;

    if (!reports.length) {
        reportList.innerHTML = `
            <div class="card border-0 p-5 shadow-sm text-center text-muted">
                <i class="bi bi-file-earmark-text fs-1 text-pink"></i>
                <p class="mt-3 mb-0">Belum ada laporan untuk tab ini.</p>
            </div>
        `;
        return;
    }

    reportList.innerHTML = reports.map(report => {
        const progress = statusProgress(report.status);
        const updatedAt = formatTimestamp(report.updated_at);
        const statusClass = statusBadgeClass(report.status);
        const editButton =
            report.is_owner &&
            report.status === 'DRAFT'
                ? `<button type="button"
                    class="btn btn-sm btn-warning"
                    onclick="editDraft(${report.id})">
                    Edit Draft
                </button>`
        : '';
        const deleteButton = report.is_owner
            ? `<button type="button" class="btn btn-sm btn-danger" onclick="deleteDraft(${report.id})">Hapus</button>`
            : '';
        const detailButton = `<button type="button" class="btn btn-sm btn-info" onclick="viewDetail(${report.id})">Detail</button>`;

        return `
            <div class="card mb-3 shadow-sm">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
                        <div>
                            <h5 class="card-title mb-1">${report.title}</h5>
                            <p class="mb-1 text-muted small">${report.category} · ${report.location}</p>
                        </div>
                        <span class="badge ${statusClass}">${report.status.replace('_', ' ')}</span>
                    </div>
                    <p class="card-text mt-3">${report.description}</p>
                    <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                        <small class="text-muted">Pelapor: ${report.reporter}</small>
                        <small class="text-muted">Terakhir diperbarui: ${updatedAt}</small>
                    </div>
                    <div class="mt-3">
                        <div class="d-flex justify-content-between mb-1">
                            <small class="text-muted">Progress</small>
                            <small class="text-muted">${progress.label}</small>
                        </div>
                        <div class="progress" style="height: 10px;">
                            <div class="progress-bar ${progress.barClass}" role="progressbar" style="width: ${progress.value}%" aria-valuenow="${progress.value}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                    </div>
                    <div class="mt-3 d-flex gap-2 flex-wrap">
                        ${editButton}
                        ${deleteButton}
                        ${detailButton}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function renderPagination(data, tab) {
    const paginationNav = document.getElementById('paginationNav');
    if (!paginationNav) return;

    const pageSize = 10;
    const totalPages = Math.ceil((data.count || 0) / pageSize);
    if (totalPages <= 1) {
        paginationNav.innerHTML = '';
        return;
    }

    let buttons = '';
    for (let page = 1; page <= totalPages; page++) {
        buttons += `
            <li class="page-item ${page === currentPage ? 'active' : ''}">
                <button type="button" class="page-link" data-page="${page}">${page}</button>
            </li>
        `;
    }

    paginationNav.innerHTML = `
        <ul class="pagination justify-content-center">
            <li class="page-item ${!data.previous ? 'disabled' : ''}">
                <button type="button" class="page-link" data-page="${Math.max(currentPage - 1, 1)}">Sebelumnya</button>
            </li>
            ${buttons}
            <li class="page-item ${!data.next ? 'disabled' : ''}">
                <button type="button" class="page-link" data-page="${Math.min(currentPage + 1, totalPages)}">Berikutnya</button>
            </li>
        </ul>
    `;

    paginationNav.querySelectorAll('button[data-page]').forEach(button => {
        button.addEventListener('click', () => {
            const page = Number(button.dataset.page);
            if (page && page !== currentPage) {
                currentPage = page;
                loadDashboardData(tab, page);
            }
        });
    });
}

async function editDraft(id) {
    try {
        const response = await requestAPI(`/api/report/${id}/`, 'GET');
        if (!response.ok) {
            alert('Gagal memuat data laporan. Silakan coba lagi.');
            return;
        }

        const data = await response.json();
        editingReportId = id;
        document.getElementById('reportModalLabel').textContent = 'Edit Laporan';
        document.getElementById('reportTitle').value = data.title || '';
        document.getElementById('reportCategory').value = data.category || '';
        document.getElementById('reportLocation').value = data.location || '';
        document.getElementById('reportDescription').value = data.description || '';

        reportModal?.show();
    } catch (error) {
        console.error('editDraft error:', error);
        alert('Terjadi kesalahan saat membuka laporan.');
    }
}



function resetReportForm() {
    const form = document.getElementById('reportForm');
    if (form) {
        form.reset();
    }
    editingReportId = null;
}

async function deleteDraft(id) {
    if (!confirm('Apakah Anda yakin ingin menghapus laporan ini?')) {
        return;
    }

    try {
        const response = await requestAPI(`/api/report/${id}/`, 'DELETE');
        if (response.status === 204) {
            alert('Laporan berhasil dihapus.');
            await loadDashboardData(currentTab, currentPage);
            return;
        }

        alert('Gagal menghapus laporan. Hanya draft yang dapat dihapus.');
    } catch (error) {
        console.error('deleteDraft error:', error);
        alert('Terjadi kesalahan saat menghapus laporan.');
    }
}

async function viewDetail(id) {
    try {
        const response = await requestAPI(`/api/report/${id}/`, 'GET');
        if (!response.ok) {
            alert('Gagal memuat detail laporan.');
            return;
        }

        const data = await response.json();
        alert(`
DETAIL LAPORAN

Judul: ${data.title}
Kategori: ${data.category}
Lokasi: ${data.location}
Status: ${data.status}
Pelapor: ${data.reporter}

Deskripsi:
${data.description}

Dibuat: ${formatTimestamp(data.created_at)}
Diperbarui: ${formatTimestamp(data.updated_at)}
        `);
    } catch (error) {
        console.error('viewDetail error:', error);
        alert('Terjadi kesalahan saat memuat detail laporan.');
    }
}

async function submitReport(status) {
    const title = document.getElementById('reportTitle')?.value.trim();
    const category = document.getElementById('reportCategory')?.value.trim();
    const location = document.getElementById('reportLocation')?.value.trim();
    const description = document.getElementById('reportDescription')?.value.trim();

    if (!title || !category || !location || !description) {
        alert('Semua field harus diisi.');
        return;
    }

    const payload = { title, category, location, description, status };
    const endpoint = editingReportId ? `/api/report/${editingReportId}/` : '/api/report/';
    const method = editingReportId ? 'PUT' : 'POST';

    try {
        const response = await requestAPI(endpoint, method, payload);
        if ([200, 201].includes(response.status)) {
            reportModal?.hide();
            resetReportForm();
            editingReportId = null;
            await loadDashboardData(currentTab, currentPage);
            alert('Laporan berhasil disimpan.');
            return;
        }

        const errorData = await response.json();
        console.error('submitReport error response:', errorData);
        alert('Gagal menyimpan laporan. Periksa kembali input Anda.');
    } catch (error) {
        console.error('submitReport error:', error);
        alert('Gagal mengirim data ke server. Cek koneksi backend.');
    }
}

window.setupDashboard = setupDashboard;
window.openReportModal = () => {
    editingReportId = null;
    document.getElementById('reportModalLabel').textContent = 'Tambah Laporan Baru';
    resetReportForm();
    if (!reportModal) {
        const modalElement = document.getElementById('reportModal');
        if (modalElement) {
            reportModal = new bootstrap.Modal(modalElement);
        }
    }
    reportModal?.show();
};
window.editDraft = editDraft;
window.deleteDraft = deleteDraft;
window.viewDetail = viewDetail;
window.submitReport = submitReport;