// js/auth.js
function setupLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const usernameInput = document.getElementById('loginUsername').value;
        const passwordInput = document.getElementById('loginPassword').value;

        const payload = { username: usernameInput, password: passwordInput };

        try {
            const response = await requestAPI('/api/token/', 'POST', payload);

            if (response.status === 200) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);

                alert('Login Berhasil di Bandung City Portal!');
                window.location.hash = '#dashboard';
            } else {
                alert('Login Gagal! Periksa kembali username dan password Anda.');
            }
        } catch (error) {
            alert('Gagal terhubung ke server backend.');
        }
    });
}