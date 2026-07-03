// js/router.js

const routes = {
    '#login': `
        <div class="row justify-content-center mt-5">
            <div class="col-md-4 card shadow-sm border-0 p-4">
                <h4 class="text-center fw-bold mb-4 text-pink">Login Warga Bandung City</h4>
                <form id="loginForm">
                    <div class="mb-3">
                        <input type="text" id="loginUsername" class="form-control mb-3" placeholder="Username" required>
                    </div>
                    <div class="mb-3">
                        <input type="password" id="loginPassword" class="form-control mb-3" placeholder="Password" required>
                    </div>
                    <button type="submit" class="btn btn-pink w-100 fw-bold">Masuk</button>
                </form>
            </div>
        </div>
    `,
    '#dashboard': `
        <div class="row g-4">
            <aside class="col-12 col-lg-3">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px;">
                    <button id="openReportModalBtn" type="button" class="btn btn-pink btn-lg w-100 fw-bold mb-2">
                        <i class="bi bi-plus-circle-fill me-2"></i>Tambah Laporan Baru
                    </button>
                    <!-- Alias tombol yang sama, dipakai oleh sebagian skenario E2E -->
                    <button id="btnBukaModal" type="button" class="btn btn-outline-pink btn-sm w-100 fw-bold mb-3">
                        <i class="bi bi-plus-circle me-2"></i>Buat Laporan
                    </button>

                    <div class="mb-3" id="summaryStats">
                        <h6 class="text-uppercase text-muted mb-3">Rekap Status</h6>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>Draft</span><span class="badge bg-warning text-dark" id="summaryDraft">0</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>Diproses</span><span class="badge bg-secondary" id="summaryInProgress">0</span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span>Selesai</span><span class="badge bg-success" id="summaryResolved">0</span>
                        </div>
                    </div>
                </div>
            </aside>

            <section class="col-12 col-lg-6">
                <div class="card border-0 p-3 shadow-sm mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <div class="nav nav-pills" id="dashboardTabs" role="tablist"></div>
                        <button id="logoutBtn" class="btn btn-outline-secondary btn-sm">Logout</button>
                    </div>
                    <div id="listContainer" class="row"></div>
                    <nav aria-label="Pagination" id="paginationContainer"></nav>
                </div>

                <div class="card border-0 p-3 shadow-sm mb-4">
                    <h6 class="fw-bold text-pink mb-3">Grafik Statistik</h6>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <canvas id="statusChart" height="220"></canvas>
                        </div>
                        <div class="col-md-6 mb-3">
                            <canvas id="categoryChart" height="220"></canvas>
                        </div>
                    </div>
                </div>

                <div class="card border-0 p-3 shadow-sm mb-4">
                    <h6 class="fw-bold text-pink mb-2">Laporan Berjalan</h6>
                    <div class="table-responsive mb-4">
                        <table id="reportedTable" class="table table-sm align-middle">
                            <thead>
                                <tr><th>Judul</th><th>Kategori</th><th>Status</th></tr>
                            </thead>
                            <tbody id="reportedTableBody"></tbody>
                        </table>
                    </div>

                    <h6 class="fw-bold text-pink mb-2">Laporan Selesai</h6>
                    <div class="table-responsive">
                        <table id="resolvedTable" class="table table-sm align-middle">
                            <thead>
                                <tr><th>Judul</th><th>Kategori</th><th>Status</th></tr>
                            </thead>
                            <tbody id="resolvedTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </section>

            <aside class="col-lg-3 d-none d-lg-block">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px;">
                    <h5 class="fw-bold text-pink"><i class="bi bi-info-circle-fill me-2"></i>Petunjuk</h5>
                    <p class="small text-muted">Pilih tab untuk melihat Laporan Saya atau Feed Kota. Tombol tambah akan membuka modal form tanpa reload.</p>
                </div>
            </aside>
        </div>

        <!-- Modal Tambah/Edit Laporan -->
        <div class="modal fade" id="reportModal" tabindex="-1" aria-labelledby="reportModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="reportModalLabel">Buat Laporan Baru</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <form id="reportForm">
                            <div class="mb-3">
                                <label for="inputTitle" class="form-label">Judul Laporan</label>
                                <input type="text" id="inputTitle" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label for="inputCategory" class="form-label">Kategori</label>
                                <select id="inputCategory" class="form-select" required>
                                    <option value="">Pilih Kategori</option>
                                    <option value="Infrastruktur">Infrastruktur</option>
                                    <option value="Kebersihan">Kebersihan</option>
                                    <option value="Keamanan">Keamanan</option>
                                    <option value="Lainnya">Lainnya</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="inputLocation" class="form-label">Lokasi Kejadian</label>
                                <input type="text" id="inputLocation" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label for="inputDescription" class="form-label">Deskripsi</label>
                                <textarea id="inputDescription" class="form-control" rows="4" required></textarea>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" id="btnDraft" class="btn btn-outline-secondary">Simpan Draft</button>
                        <button type="button" id="btnSubmit" class="btn btn-pink">Kirim Laporan</button>
                    </div>
                </div>
            </div>
        </div>
    `,
    '#reports': `
        <div class="card border-0 p-3 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="fw-bold text-pink mb-0">Cari Laporan</h5>
                <button id="logoutBtnReports" class="btn btn-outline-secondary btn-sm">Logout</button>
            </div>
            <input type="text" id="searchInput" class="form-control mb-3" placeholder="Cari judul laporan...">
            <div class="table-responsive">
                <table id="reportedTable" class="table table-sm align-middle">
                    <thead>
                        <tr><th>Judul</th><th>Kategori</th><th>Lokasi</th><th>Status</th></tr>
                    </thead>
                    <tbody id="reportTableBody"></tbody>
                </table>
            </div>
        </div>
    `
};

// #dashboard dan #reports sama-sama butuh token, jadi keduanya dilindungi auth guard.
const PROTECTED_ROUTES = ['#dashboard', '#reports'];

function handleRouting() {
    const hash = window.location.hash || '#login';
    const contentDiv = document.getElementById('app-content');

    if (PROTECTED_ROUTES.includes(hash) && !localStorage.getItem('access_token')) {
        window.location.hash = '#login';
        return;
    }

    if (hash === '#login' && localStorage.getItem('access_token')) {
        window.location.hash = '#dashboard';
        return;
    }

    contentDiv.innerHTML = routes[hash] || routes['#login'];

    if (hash === '#login') {
        if (typeof setupLoginForm === 'function') {
            setupLoginForm();
        }
    }

    if (hash === '#dashboard') {
        if (typeof setupDashboard === 'function') {
            setupDashboard();
        }
    }

    if (hash === '#reports') {
        if (typeof setupReportsPage === 'function') {
            setupReportsPage();
        }
    }
}

window.addEventListener('hashchange', handleRouting);
window.addEventListener('DOMContentLoaded', handleRouting);
