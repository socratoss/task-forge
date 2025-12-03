document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = e.target.email.value;
    const password = e.target.password.value;

    try {
        const response = await fetch('https://твой-сервер.com/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert('Login succeeded!');
            // Например: window.location.href = '/dashboard.html';
        } else {
            alert(data.message || 'Login error');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Server connection failed');
    }
});