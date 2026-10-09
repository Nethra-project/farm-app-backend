const API_BASE_URL = 'http://127.0.0.1:5000';
let currentLang = 'en';
let currentUser = null;
let currentRoleType = null;

// Translation Dictionary
const i18n = {
    en: {
        appTitle: "🌾 Krishi Bazaar",
        heroTitle: "Direct Agricultural Marketplace",
        heroDesc: "Connecting Farmers, FPOs, Consumers, Bulk Buyers, and Drivers seamlessly.",
        btnSignup: "Sign Up",
        btnLogin: "Log In",
        selectRole: "Choose Interface / Role",
        loginHeading: "Account Login"
    },
    hi: {
        appTitle: "🌾 कृषि बाजार",
        heroTitle: "प्रत्यक्ष कृषि बाजार",
        heroDesc: "किसानों, एफपीओ, उपभोक्ताओं, थोक खरीदारों और ड्राइवरों को निर्बाध रूप से जोड़ना।",
        btnSignup: "साइन अप करें",
        btnLogin: "लॉग इन करें",
        selectRole: "इंटरफ़ेस / भूमिका चुनें",
        loginHeading: "खाता लॉगिन"
    }
};

function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'hi' : 'en';
    document.getElementById('current-lang').innerText = currentLang === 'en' ? 'English' : 'हिंदी';
    
    document.getElementById('txt-app-title').innerText = i18n[currentLang].appTitle;
    document.getElementById('txt-hero-title').innerText = i18n[currentLang].heroTitle;
    document.getElementById('txt-hero-desc').innerText = i18n[currentLang].heroDesc;
    document.getElementById('txt-btn-signup').innerText = i18n[currentLang].btnSignup;
    document.getElementById('txt-btn-login').innerText = i18n[currentLang].btnLogin;
    document.getElementById('txt-select-role').innerText = i18n[currentLang].selectRole;
    document.getElementById('txt-login-heading').innerText = i18n[currentLang].loginHeading;
}

function showView(viewId) {
    document.querySelectorAll('.view-section').forEach(v => {
        if(v.id !== 'console-output-container') v.classList.remove('active');
    });
    document.getElementById(viewId).classList.add('active');
}

function logConsole(data) {
    document.getElementById('console-output').innerText = JSON.stringify(data, null, 2);
}

// Render Specific Signup Forms
function setupSignupForm(role) {
    currentRoleType = role;
    const container = document.getElementById('signup-fields');
    document.getElementById('signup-title').innerText = `${role.replace('_', ' ').toUpperCase()} Registration`;
    
    let html = `
        <input type="text" id="su-name" placeholder="Full Name / Entity Name">
        <input type="text" id="su-phone" placeholder="Mobile Number">
        <input type="password" id="su-pass" placeholder="Password">
    `;

    if (role === 'farmer') {
        html += `
            <input type="text" id="su-village" placeholder="Village">
            <input type="text" id="su-district" placeholder="District">
            <input type="text" id="su-state" placeholder="State">
            <input type="text" id="su-pincode" placeholder="Pincode">
            <input type="text" id="su-crops" placeholder="Crops Grown (e.g. Tomatoes, Wheat)">
            <input type="text" id="su-bank" placeholder="UPI ID or Bank Account & IFSC">
            <input type="text" id="su-fpo" placeholder="FPO Name (Optional)">
        `;
    } else if (role === 'fpo') {
        html += `
            <input type="text" id="su-fpo-reg" placeholder="Registration Type & Number">
            <input type="text" id="su-district" placeholder="District">
            <input type="text" id="su-state" placeholder="State">
            <input type="text" id="su-pincode" placeholder="Pincode">
            <input type="text" id="su-contact" placeholder="Contact Person Name & Designation">
            <input type="text" id="su-bank" placeholder="Bank Account & IFSC">
        `;
    } else if (role === 'consumer') {
        html += `
            <input type="text" id="su-address" placeholder="Delivery Address, Landmark">
            <input type="text" id="su-city" placeholder="City">
            <input type="text" id="su-pincode" placeholder="Pincode">
        `;
    } else if (role === 'bulk_buyer') {
        html += `
            <input type="text" id="su-biz-name" placeholder="Business Name">
            <select id="su-biz-type">
                <option value="hotel">Hotel</option>
                <option value="restaurant">Restaurant</option>
                <option value="mess">Mess / Canteen</option>
                <option value="retailer">Retailer</option>
                <option value="processor">Processor</option>
            </select>
            <input type="text" id="su-gstin" placeholder="GSTIN (Optional)">
            <input type="text" id="su-address" placeholder="Delivery Address, City, Pincode">
            <input type="text" id="su-qty" placeholder="Crops Needed & Approx Monthly Qty">
        `;
    } else if (role === 'driver') {
        html += `
            <input type="text" id="su-city" placeholder="City & Served Districts/Pincodes">
            <select id="su-vehicle-type">
                <option value="bike">Bike</option>
                <option value="tempo">Tempo</option>
                <option value="pickup_truck">Pickup Truck</option>
                <option value="mini_truck">Mini Truck</option>
            </select>
            <input type="text" id="su-vehicle-no" placeholder="Vehicle Number">
            <input type="number" id="su-capacity" placeholder="Load Capacity (kg)">
            <input type="text" id="su-bank" placeholder="UPI ID / Bank Payout Details">
        `;
    }

    container.innerHTML = html;
    document.getElementById('otp-section').style.display = 'block';
    showView('view-signup');
}

// Registration Submit Execution
async function submitSignup() {
    const phone = document.getElementById('su-phone').value;
    const password = document.getElementById('su-pass').value;
    const name = document.getElementById('su-name').value;

    let endpoint = `${API_BASE_URL}/auth/register`;
    let payload = { phone, password, role: currentRoleType, full_name: name };

    if (currentRoleType === 'consumer' || currentRoleType === 'bulk_buyer') {
        endpoint = `${API_BASE_URL}/buyer/auth/signup`;
        payload.buyer_type = currentRoleType === 'consumer' ? 'consumer' : 'bulk_buyer';
        payload.full_name_or_contact = name;
    } else if (currentRoleType === 'driver') {
        endpoint = `${API_BASE_URL}/driver/auth/signup`;
        payload.full_name = name;
        payload.city = document.getElementById('su-city')?.value || 'City';
        payload.district = 'District A';
        payload.pincodes_served = '110001';
        payload.vehicle_type = document.getElementById('su-vehicle-type')?.value || 'tempo';
        payload.vehicle_number = document.getElementById('su-vehicle-no')?.value || 'REG123';
        payload.load_capacity_kg = parseFloat(document.getElementById('su-capacity')?.value || 500);
    }

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        logConsole(data);
        if (data.status === 'success') {
            alert("Registration complete! Please log in.");
            showView('view-login');
        }
    } catch (err) {
        logConsole({ status: "error", message: "Failed to connect to backend API." });
    }
}

// Login Handler
async function handleLogin() {
    const phone = document.getElementById('login-phone').value;
    const password = document.getElementById('login-pass').value;

    try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, password })
        });
        const data = await res.json();
        logConsole(data);

        if (data.status === 'success') {
            currentUser = data.data;
            document.getElementById('logout-btn').style.display = 'inline-block';
            loadDashboard(currentUser.role, currentUser.approval_status || 'pending');
        } else {
            alert(data.message || "Login failed");
        }
    } catch (err) {
        logConsole({ status: "error", message: "Backend communication error." });
    }
}

function handleLogout() {
    currentUser = null;
    document.getElementById('logout-btn').style.display = 'none';
    showView('view-landing');
}

// Construct Role Dashboards
function loadDashboard(role, status) {
    showView('view-dashboard');
    const nav = document.getElementById('dash-nav-buttons');
    const content = document.getElementById('dash-main-content');
    const warning = document.getElementById('approval-warning');

    if (status === 'pending') {
        warning.style.display = 'block';
    } else {
        warning.style.display = 'none';
    }

    if (role === 'farmer' || role === 'fpo') {
        nav.innerHTML = `
            <button onclick="renderFarmerOverview()">Summary Dashboard</button>
            <button onclick="renderAddListing()" ${status === 'pending' ? 'disabled title="Approval pending"' : ''}>Add Listing</button>
            <button onclick="fetchListings()">View Active Listings</button>
            <button onclick="fetchMandiPrices()">Mandi Prices</button>
        `;
        renderFarmerOverview();
    } else if (role === 'buyer') {
        nav.innerHTML = `
            <button onclick="renderBuyerOverview()">Marketplace</button>
            <button onclick="fetchRFQs()">Bulk RFQs</button>
            <button onclick="fetchOrders()">My Orders</button>
        `;
        renderBuyerOverview();
    } else if (role === 'driver') {
        nav.innerHTML = `
            <button onclick="renderDriverJobs()">Available Delivery Jobs</button>
            <button onclick="renderDriverEarnings()">My Earnings</button>
        `;
        renderDriverJobs();
    } else if (role === 'admin') {
        nav.innerHTML = `
            <button onclick="renderAdminVerifications()">Verification Queue</button>
            <button onclick="renderAdminSystem()">System Settings</button>
        `;
        renderAdminVerifications();
    }
}

// Renderers
function renderFarmerOverview() {
    document.getElementById('dash-main-content').innerHTML = `
        <div class="card">
            <h3>Welcome Farmer / FPO</h3>
            <p>Account Status: <strong>${currentUser ? currentUser.approval_status || 'pending' : 'pending'}</strong></p>
            <button class="action-btn" onclick="fetchMandiPrices()">Check Today's Mandi Rates</button>
        </div>
    `;
}

function renderAddListing() {
    document.getElementById('dash-main-content').innerHTML = `
        <div class="card" style="max-width:500px;">
            <h3>Step 6: Add Crop Listing</h3>
            <input type="text" id="lst-crop" placeholder="Crop & Variety">
            <input type="number" id="lst-qty" placeholder="Quantity">
            <input type="text" id="lst-unit" value="kg" placeholder="Unit">
            <select id="lst-grade"><option value="A">Grade A</option><option value="B">Grade B</option><option value="C">Grade C</option></select>
            <input type="number" step="0.01" id="lst-price" placeholder="Asking Price per kg">
            <input type="text" id="lst-district" placeholder="Pickup District">
            <button class="action-btn" onclick="submitListing()">Publish Listing</button>
        </div>
    `;
}

async function submitListing() {
    const payload = {
        crop_name: document.getElementById('lst-crop').value,
        quantity: parseFloat(document.getElementById('lst-qty').value),
        unit: document.getElementById('lst-unit').value,
        price_per_unit: parseFloat(document.getElementById('lst-price').value),
        district: document.getElementById('lst-district').value,
        category: 'vegetables'
    };
    try {
        const res = await fetch(`${API_BASE_URL}/listings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        logConsole(await res.json());
    } catch (err) {
        logConsole({ status: 'error', message: 'Failed to post listing.' });
    }
}

async function fetchListings() {
    try {
        const res = await fetch(`${API_BASE_URL}/listings`);
        const data = await res.json();
        logConsole(data);
        document.getElementById('dash-main-content').innerHTML = `<div class="card"><h3>Active Marketplace Listings</h3><pre>${JSON.stringify(data.data, null, 2)}</pre></div>`;
    } catch (err) {
        logConsole({ status: 'error', message: 'Failed to fetch listings.' });
    }
}

async function fetchMandiPrices() {
    try {
        const res = await fetch(`${API_BASE_URL}/utils/mandi-prices`);
        const data = await res.json();
        logConsole(data);
        document.getElementById('dash-main-content').innerHTML = `<div class="card"><h3>Today's Mandi Prices</h3><pre>${JSON.stringify(data.data, null, 2)}</pre></div>`;
    } catch (err) {
        logConsole({ status: 'error', message: 'Failed to fetch mandi prices.' });
    }
}

function renderBuyerOverview() {
    document.getElementById('dash-main-content').innerHTML = `
        <div class="card">
            <h3>Consumer & Bulk Buyer Portal</h3>
            <button class="action-btn" onclick="fetchListings()">Browse All Listings</button>
        </div>
    `;
}

async function fetchRFQs() {
    try {
        const res = await fetch(`${API_BASE_URL}/buyer/rfqs`);
        const data = await res.json();
        logConsole(data);
        document.getElementById('dash-main-content').innerHTML = `<div class="card"><h3>Open Bulk RFQs</h3><pre>${JSON.stringify(data.data, null, 2)}</pre></div>`;
    } catch (err) {
        logConsole({ status: 'error', message: 'Failed to fetch RFQs.' });
    }
}

function renderDriverJobs() {
    document.getElementById('dash-main-content').innerHTML = `
        <div class="card">
            <h3>Pickup & Delivery Jobs</h3>
            <button class="action-btn" onclick="fetchJobs()">Search Nearby Jobs</button>
        </div>
    `;
}

async function fetchJobs() {
    try {
        const res = await fetch(`${API_BASE_URL}/driver/jobs`);
        const data = await res.json();
        logConsole(data);
        document.getElementById('dash-main-content').innerHTML = `<div class="card"><h3>Available Jobs</h3><pre>${JSON.stringify(data.data, null, 2)}</pre></div>`;
    } catch (err) {
        logConsole({ status: 'error', message: 'Failed to fetch jobs.' });
    }
}

function renderAdminVerifications() {
    document.getElementById('dash-main-content').innerHTML = `
        <div class="card">
            <h3>Admin Verification Queue</h3>
            <p>Reviewing submitted registrations for Farmers, FPOs, Bulk Buyers, and Drivers.</p>
        </div>
    `;
}

function renderAdminSystem() {
    document.getElementById('dash-main-content').innerHTML = `
        <div class="card">
            <h3>System Settings</h3>
            <p>Platform Fees, Transport Rates & District Controls.</p>
        </div>
    `;
}
