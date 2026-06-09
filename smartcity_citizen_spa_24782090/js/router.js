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
                    <button id="openReportModalBtn" type="button" class="btn btn-pink btn-lg w-100 fw-bold mb-3" onclick="openReportModal()">
                        <i class="bi bi-plus-circle-fill me-2"></i>Tambah Laporan Baru
                    </button>
                    <div class="mb-3">
                        <h6 class="text-uppercase text-muted mb-3">Rekap Status</h6>
                        <div class="d-flex justify-content-between mb-2">
                            <span>Draft</span><strong id="summaryDraft">0</strong>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span>Diproses</span><strong id="summaryInProgress">0</strong>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span>Selesai</span><strong id="summaryResolved">0</strong>
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
                    <div id="reportList"></div>
                    <nav aria-label="Pagination" id="paginationNav"></nav>
                </div>
            </section>

            <aside class="col-lg-3 d-none d-lg-block">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px;">
                    <h5 class="fw-bold text-pink"><i class="bi bi-info-circle-fill me-2"></i>Petunjuk</h5>
                    <p class="small text-muted">Pilih tab untuk melihat Laporan Saya atau Feed Kota. Tombol tambah akan membuka modal form tanpa reload.</p>
                </div>
            </aside>
        </div>

    `
};

function handleRouting() {
    const hash = window.location.hash || '#login';
    const contentDiv = document.getElementById('app-content');

    if (hash === '#dashboard' && !localStorage.getItem('access_token')) {
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
}

window.addEventListener('hashchange', handleRouting);
window.addEventListener('DOMContentLoaded', handleRouting);