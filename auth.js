document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const payload = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            role: document.getElementById('role').value,
        };

        try {
            const result = await apiRequest('/api/auth/login', {
                method: 'POST',
                body: payload,
            });
            if (result.success) {
                sessionStorage.setItem('currentUser', JSON.stringify(result.user));
                window.location.href = '/dashboard';
            } else {
                showToast(result.message || 'Login failed', 'error');
            }
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
});

async function checkAuth() {
    try {
        const result = await apiRequest('/api/auth/me');
        if (!result.success) {
            window.location.href = '/login';
        }
    } catch (error) {
        window.location.href = '/login';
    }
}
