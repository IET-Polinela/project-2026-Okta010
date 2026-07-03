// js/app.js
console.log("Bandung City Citizen SPA (NPM: 24782090) Berhasil Dimuat.");

let currentTab = 'my_reports';
let currentPage = 1;
let editingReportId = null;
let reportModal = null;
let statusChartInstance = null;
let categoryChartInstance = null;

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
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('id-ID', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// ---------------------------------------------------------------------------
// Chart.js: dimuat secara dinamis (CDN) agar tidak perlu mengubah index.html.
// ---------------------------------------------------------------------------
function loadChartJsLibrary() {
    return new Promise((resolve, reject) => {
        if (window.Chart) {
            resolve();
            return;
        }
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js';
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('Gagal memuat Chart.js dari CDN'));
        document.head.appendChild(script);
    });
}

async function renderCharts(reports) {
    try {
        await loadChartJsLibrary();
    } catch (error) {
        console.error('renderCharts:', error);
        return;
    }

    const statusCanvas = document.getElementById('statusChart');
    const categoryCanvas = document.getElementById('categoryChart');
    if (!statusCanvas || !categoryCanvas || !window.Chart) return;

    const statusCounts = {};
    const categoryCounts = {};
    reports.forEach(report => {
        const status = report.status || 'UNKNOWN';
        const category = report.category || 'Lainnya';
        statusCounts[status] = (statusCounts[status] || 0) + 1;
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });

    if (statusChartInstance) {
        statusChartInstance.destroy();
    }
    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    statusChartInstance = new window.Chart(statusCanvas, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusCounts),
            datasets: [{
                data: Object.values(statusCounts),
                backgroundColor: ['#ffc107', '#0dcaf0', '#0d6efd', '#6c757d', '#198754', '#adb5bd']
            }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });

    categoryChartInstance = new window.Chart(categoryCanvas, {
        type: 'bar',
        data: {
            labels: Object.keys(categoryCounts),
            datasets: [{
                label: 'Jumlah Laporan',
                data: Object.values(categoryCounts),
                backgroundColor: '#e91e8c'
            }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}

function populateStatusTables(reports) {
    const reportedBody = document.getElementById('reportedTableBody');
    const resolvedBody = document.getElementById('resolvedTableBody');
    if (!reportedBody || !resolvedBody) return;

    const reported = reports.filter(r => r.status !== 'RESOLVED' && r.status !== 'DRAFT');
    const resolved = reports.filter(r => r.status === 'RESOLVED');

    const rowHtml = r => `
        <tr>
            <td>${r.title || '-'}</td>
            <td>${r.category || '-'}</td>
            <td>${(r.status || '-').replace('_', ' ')}</td>
        </tr>
    `;

    reportedBody.innerHTML = reported.length
        ? reported.map(rowHtml).join('')
        : '<tr><td colspan="3" class="text-center text-muted">Tidak ada laporan berjalan.</td></tr>';

    resolvedBody.innerHTML = resolved.length
        ? resolved.map(rowHtml).join('')
        : '<tr><td colspan="3" class="text-center text-muted">Belum ada laporan selesai.</td></tr>';
}

// setupDashboard: pasang semua event listener halaman dashboard lalu muat data awal.
async function setupDashboard() {
    const dashboardTabs = document.getElementById('dashboardTabs');
    if (dashboardTabs) {
        const tabDefs = [
            { key: 'my_reports', label: 'Laporan Saya', id: 'tabMyReports' },
            { key: 'feed', label: 'Feed Kota', id: 'tabFeedKota' }
        ];

        dashboardTabs.innerHTML = tabDefs.map(tab => `
            <button type="button" id="${tab.id}" class="nav-link ${tab.key === currentTab ? 'active' : ''}" data-tab="${tab.key}">
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
    const openButtonAlias = document.getElementById('btnBukaModal');
    const logoutButton = document.getElementById('logoutBtn');
    const saveDraftButton = document.getElementById('btnDraft');
    const submitReportButton = document.getElementById('btnSubmit');

    const modalElement = document.getElementById('reportModal');
    if (modalElement) {
        reportModal = new bootstrap.Modal(modalElement);
    }

    openButton?.addEventListener('click', () => openReportModal());
    openButtonAlias?.addEventListener('click', () => openReportModal());

    logoutButton?.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.hash = '#login';
    });

    saveDraftButton?.addEventListener('click', () => submitReport('DRAFT'));
    submitReportButton?.addEventListener('click', () => submitReport('REPORTED'));

    await loadDashboardData(currentTab, currentPage);
}

// Ambil daftar laporan terpaginasi lalu perbarui UI dengan renderList dan renderPagination.
async function loadDashboardData(tab = 'my_reports', page = 1) {
    currentTab = tab;
    currentPage = page;

    const listContainer = document.getElementById('listContainer');

    if (listContainer) {
        listContainer.innerHTML = '<div class="col-12 text-center py-5 text-muted">Memuat data laporan...</div>';
    }

    try {
        const response = await requestAPI(`/api/report/?tab=${tab}&page=${page}`);

        if (response.status === 401) {
            alert('Token tidak valid. Silakan login ulang.');
            localStorage.clear();
            window.location.hash = '#login';
            return;
        }

        const data = await response.json();
        const reports = data.results || [];

        renderList(reports, tab);
        renderPagination(data, tab);
    } catch (error) {
        if (listContainer) {
            listContainer.innerHTML = '<div class="col-12"><div class="alert alert-danger">Gagal memuat laporan. Cek koneksi backend.</div></div>';
        }
        console.error('loadDashboardData error:', error);
    }

    // Ringkasan statistik & grafik dimuat terpisah agar tetap tampil
    // walaupun daftar laporan di atas gagal dimuat.
    await loadSummaryStats();
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

        populateStatusTables(reports);
        await renderCharts(reports);
    } catch (error) {
        console.error('loadSummaryStats error:', error);
    }
}

function renderList(reports, tab) {
    const listContainer = document.getElementById('listContainer');
    if (!listContainer) return;

    if (!reports.length) {
        listContainer.innerHTML = `
            <div class="col-12">
                <div class="card border-0 p-5 shadow-sm text-center text-muted">
                    <i class="bi bi-file-earmark-text fs-1 text-pink"></i>
                    <p class="mt-3 mb-0">Belum ada laporan untuk tab ini.</p>
                </div>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = reports.map(report => {
        const progress = statusProgress(report.status);
        const updatedAt = formatTimestamp(report.updated_at);
        const statusClass = statusBadgeClass(report.status);
        const reporterName = report.reporter_name || report.reporter || '-';
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
            <div class="col">
                <div class="card mb-3 shadow-sm h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
                            <div>
                                <h5 class="card-title mb-1">${report.title || '-'}</h5>
                                <p class="mb-1 text-muted small">${report.category || '-'} · ${report.location || '-'}</p>
                            </div>
                            <span class="badge ${statusClass}">${(report.status || '-').replace('_', ' ')}</span>
                        </div>
                        <p class="card-text mt-3">${report.description || ''}</p>
                        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                            <small class="text-muted">Pelapor: ${reporterName}</small>
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
            </div>
        `;
    }).join('');
}

function renderPagination(data, tab) {
    const paginationContainer = document.getElementById('paginationContainer');
    if (!paginationContainer) return;

    const pageSize = 10;
    const totalPages = Math.ceil((data.count || 0) / pageSize);
    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
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

    paginationContainer.innerHTML = `
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

    paginationContainer.querySelectorAll('button[data-page]').forEach(button => {
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
        document.getElementById('inputTitle').value = data.title || '';
        document.getElementById('inputCategory').value = data.category || '';
        document.getElementById('inputLocation').value = data.location || '';
        document.getElementById('inputDescription').value = data.description || '';

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
Pelapor: ${data.reporter_name || data.reporter || '-'}

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
    const title = document.getElementById('inputTitle')?.value.trim();
    const category = document.getElementById('inputCategory')?.value.trim();
    const location = document.getElementById('inputLocation')?.value.trim();
    const description = document.getElementById('inputDescription')?.value.trim();

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
            alert(`Laporan berhasil disimpan sebagai ${status}.`);
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

// ---------------------------------------------------------------------------
// Halaman #reports: pencarian laporan (live search)
// ---------------------------------------------------------------------------
function renderSearchResults(results) {
    const tbody = document.getElementById('reportTableBody');
    if (!tbody) return;

    if (!results || !results.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Tidak ada hasil.</td></tr>';
        return;
    }

    tbody.innerHTML = results.map(r => `
        <tr>
            <td>${r.title || '-'}</td>
            <td>${r.category || '-'}</td>
            <td>${r.location || '-'}</td>
            <td>${(r.status || '-').replace('_', ' ')}</td>
        </tr>
    `).join('');
}

async function loadAllReportsForSearch() {
    try {
        const response = await requestAPI('/api/report/?tab=my_reports&page_size=1000');
        const data = await response.json();
        return data.results || [];
    } catch (error) {
        console.error('loadAllReportsForSearch error:', error);
        return [];
    }
}

function setupReportsPage() {
    const searchInput = document.getElementById('searchInput');
    const logoutBtnReports = document.getElementById('logoutBtnReports');

    logoutBtnReports?.addEventListener('click', () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.hash = '#login';
    });

    if (!searchInput) return;

    // Tampilkan semua laporan saat halaman pertama kali dibuka.
    loadAllReportsForSearch().then(renderSearchResults);

    searchInput.addEventListener('keyup', async function () {
        const query = this.value.trim();
        try {
            // NOTE: endpoint /search/ ini disediakan oleh backend Django,
            // bukan bagian dari file-file frontend ini.
            const response = await fetch(`${BASE_URL}/search/?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            renderSearchResults(data.results || []);
        } catch (error) {
            console.error('search error:', error);
        }
    });
}

window.setupDashboard = setupDashboard;
window.setupReportsPage = setupReportsPage;
window.openReportModal = () => {
    editingReportId = null;
    document.getElementById('reportModalLabel').textContent = 'Buat Laporan Baru';
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