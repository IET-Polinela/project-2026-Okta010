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
                    <button class="btn btn-pink btn-lg w-100 fw-bold mb-3">
                        <i class="bi bi-plus-circle-fill me-2"></i>Laporan Baru
                    </button>
                </div>
            </aside>

            <section class="col-12 col-lg-6">
                <div class="card border-0 p-5 shadow-sm text-center text-muted border-dashed" style="border: 2px dashed #ff69b4;">
                    <i class="bi bi-inbox fs-1 text-pink"></i>
                    <h5 class="mt-2 text-dark fw-bold">Selamat Datang di Bandung City Portal!</h5>
                    <p class="small">Koneksi API untuk data laporan akan diimplementasikan pada Lab 12.</p>
                </div>
            </section>

            <aside class="col-lg-3 d-none d-lg-block">
                <div class="card border-0 p-3 shadow-sm sticky-top" style="top: 20px;">
                    <h5 class="fw-bold text-pink"><i class="bi bi-info-circle-fill me-2"></i>Pengumuman</h5>
                    <p class="small text-muted">Aplikasi dalam masa pengembangan infrastruktur Bandung Smart City.</p>
                </div>
            </aside>
        </div>
    `
};

function handleRouting() {
    const hash = window.location.hash || '#login';
    const contentDiv = document.getElementById('app-content');
    
    contentDiv.innerHTML = routes[hash] || routes['#login'];

    if (hash === '#login') {
        if (typeof setupLoginForm === 'function') {
            setupLoginForm();
        }
    }
}

window.addEventListener('hashchange', handleRouting);
window.addEventListener('DOMContentLoaded', handleRouting);