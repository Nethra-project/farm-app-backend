const API_BASE_URL = 'http://127.0.0.1:5000';

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

function displayResponse(data) {
    document.getElementById('console-output').innerText = JSON.stringify(data, null, 2);
}

// 1. AUTHENTICATION
async function handleRegister() {
    const phone = document.getElementById('reg-phone').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-pass').value;
    const role = document.getElementById('reg-role').value;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, email, password, role })
        });
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

async function handleLogin() {
    const phone = document.getElementById('login-phone').value;
    const password = document.getElementById('login-pass').value;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, password })
        });
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

// 2. FARMER & LISTINGS
async function createListing() {
    const payload = {
        crop_name: document.getElementById('list-crop').value,
        category: document.getElementById('list-cat').value,
        quantity: parseFloat(document.getElementById('list-qty').value),
        unit: document.getElementById('list-unit').value,
        price_per_unit: parseFloat(document.getElementById('list-price').value),
        district: document.getElementById('list-district').value,
        description: document.getElementById('list-desc').value
    };

    try {
        const res = await fetch(`${API_BASE_URL}/listings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

async function getMarketplaceListings() {
    try {
        const res = await fetch(`${API_BASE_URL}/listings`);
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

async function getMandiPrices() {
    try {
        const res = await fetch(`${API_BASE_URL}/utils/mandi-prices`);
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

// 3. FPO HUB
async function saveFPOProfile() {
    const payload = {
        fpo_name: document.getElementById('fpo-name').value,
        registration_number: document.getElementById('fpo-reg').value,
        district: document.getElementById('fpo-district').value,
        state: document.getElementById('fpo-state').value,
        pincode: document.getElementById('fpo-pincode').value,
        contact_person: document.getElementById('fpo-contact').value
    };

    try {
        const res = await fetch(`${API_BASE_URL}/fpo/profile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

// 4. BUYER & RFQs
async function createRFQ() {
    const payload = {
        crop_name: document.getElementById('rfq-crop').value,
        quantity: parseFloat(document.getElementById('rfq-qty').value),
        needed_by_date: document.getElementById('rfq-date').value,
        target_price_per_unit: parseFloat(document.getElementById('rfq-target').value),
        delivery_district: document.getElementById('rfq-district').value
    };

    try {
        const res = await fetch(`${API_BASE_URL}/buyer/rfqs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

async function fetchRFQs() {
    try {
        const res = await fetch(`${API_BASE_URL}/buyer/rfqs`);
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

// 5. DRIVER & LOGISTICS
async function fetchDeliveryJobs() {
    try {
        const res = await fetch(`${API_BASE_URL}/driver/jobs`);
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}

// 6. ADMIN
async function fetchSystemSettings() {
    try {
        const res = await fetch(`${API_BASE_URL}/admin/settings`);
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}
