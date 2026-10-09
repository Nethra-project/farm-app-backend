const API_BASE_URL = 'http://127.0.0.1:5000';

// Register User Request
async function registerUser() {
    const phone = document.getElementById('phone').value;
    const password = document.getElementById('password').value;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, password, role: 'farmer' })
        });
        const data = await res.json();
        document.getElementById('response').innerText = JSON.stringify(data, null, 2);
    } catch (err) {
        document.getElementById('response').innerText = 'Error connecting to backend server.';
    }
}

// Fetch Listings Request
async function fetchListings() {
    try {
        const res = await fetch(`${API_BASE_URL}/listings`);
        const data = await res.json();
        document.getElementById('listings-output').innerText = JSON.stringify(data.data, null, 2);
    } catch (err) {
        document.getElementById('listings-output').innerText = 'Failed to load listings.';
    }
}