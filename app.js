const API_BASE_URL = 'http://127.0.0.1:5000';
let currentLang = 'en';
let currentUser = null;
let currentRoleType = null;
let generatedOTP = null;
let isMobileVerified = false;

// Attach click listeners cleanly on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-toggle-lang').addEventListener('click', toggleLanguage);
    document.getElementById('btn-goto-signup').addEventListener('click', () => showView('view-role-select'));
    document.getElementById('btn-goto-login').addEventListener('click', () => showView('view-login'));
    document.getElementById('btn-execute-login').addEventListener('click', handleLogin);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    document.getElementById('btn-send-otp').addEventListener('click', sendOTP);
    document.getElementById('btn-verify-otp').addEventListener('click', verifyOTP);
    document.getElementById('signup-submit-btn').addEventListener('click', submitSignup);
});

function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'hi' : 'en';
    document.getElementById('btn-toggle-lang').innerText = currentLang === 'en' ? 'Language: English' : 'Language: हिंदी';
    document.getElementById('txt-app-title').innerText = currentLang === 'en' ? '🌾 Krishi Bazaar' : '🌾 कृषि बाजार';
    document.getElementById('txt-hero-title').innerText = currentLang === 'en' ? 'Direct Agricultural Marketplace' : 'प्रत्यक्ष कृषि बाजार';
    document.getElementById('txt-btn-signup').innerText = currentLang === 'en' ? 'Sign Up' : 'साइन अप करें';
    document.getElementById('txt-btn-login').innerText = currentLang === 'en' ? 'Log In' : 'लॉग इन करें';
}

function showView(viewId) {
    document.querySelectorAll('.view-section').forEach(v => {
        if (v.id !== 'console-output-container') v.classList.remove('active');
    });
    document.getElementById(viewId).classList.add('active');
}

function logConsole(data) {
    document.getElementById('console-output').innerText = JSON.stringify(data, null, 2);
}

// Render dynamic forms for all roles
function setupSignupForm(role) {
    currentRoleType = role;
    isMobileVerified = false;
    generatedOTP = null;

    const submitBtn = document.getElementById('signup-submit-btn');
    submitBtn.disabled = true;
    submitBtn.innerText = "Complete Registration (Verify Mobile First)";
    
    document.getElementById('otp-display-box').style.display = 'none';
    document.getElementById('otp-input-group').style.display = 'none';
    
    document.getElementById('signup-title').innerText = `${role.replace('_', ' ').toUpperCase()} Registration`;
    
    const container = document.getElementById('signup-fields');
    let html = `
        <input type="text" id="su-name" placeholder="Full Name / Entity / Contact Person">
        <input type="text" id="su-phone" placeholder="Mobile Number (10 digits)">
        <input type="password" id="su-pass" placeholder="Password">
    `;

    if (role === 'farmer') {
        html += `
            <input type="text" id="su-village" placeholder="Village">
            <input type="text" id="su-district" placeholder="District">
            <input type="text" id="su-state" placeholder="State">
            <input type="text" id="su-pincode" placeholder="Pincode">
            <input type="text" id="su-crops" placeholder="Crops Grown">
            <input type="text" id="su-bank" placeholder="UPI ID or Bank Account & IFSC">
            <input type="text" id="su-fpo" placeholder="FPO Name (Optional)">
        `;
    } else if (role === 'fpo') {
        html += `
            <input type="text" id="su-fpo-reg" placeholder="FPO Registration Number">
            <input type="text" id="su-district" placeholder="District">
            <input type="text" id="su-state" placeholder="State">
            <input type="text" id="su-pincode" placeholder="Pincode">
            <input type="text" id="su-contact" placeholder="Designation">
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
            <input type="text" id="su-biz-name" placeholder="Business Name (Hotel/Restaurant/Mess)">
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
            <input type="text" id="su-city" placeholder="City / Districts Served">
            <select id="su-vehicle-type">
                <option value="bike">Bike</option>
                <option value="tempo">Tempo</option>
                <option value="pickup_truck">Pickup Truck</option>
                <option value="mini_truck">Mini Truck</option>
            </select>
            <input type="text" id="su-vehicle-no" placeholder="Vehicle Number">
            <input type="number" id="su-capacity" placeholder="Load Capacity in kg">
            <input type="text" id="su-bank" placeholder="UPI ID / Bank Payout Details">
        `;
    }

    container.innerHTML = html;
    showView('view-signup');
}

// Mobile OTP Generation
function sendOTP() {
    const phone = document.getElementById('su-phone')?.value.trim();
    if (!phone || phone.length < 10) {
        alert("Please enter a valid 10-digit mobile number first.");
        return;
    }

    generatedOTP = Math.floor(100000 + Math.random() * 900000).toString();
    
    const otpBox = document.getElementById('otp-display-box');
    otpBox.style.display = 'block';
    otpBox.innerText = `📲 SMS Sent to ${phone}! Verification Code: ${generatedOTP}`;

    document.getElementById('otp-input-group').style.display = 'block';
    logConsole({ action: "OTP_SENT", phone: phone, mock_otp: generatedOTP });
}

// Mobile OTP Verification
function verifyOTP() {
    const entered = document.getElementById('su-otp-input')?.value.trim();
    
    if (entered === generatedOTP && generatedOTP !== null) {
        isMobileVerified = true;
        alert("Mobile number verified successfully!");
        
        const otpBox = document.getElementById('otp-display-box');
        otpBox.className = "badge-verified";
        otpBox.innerText = "✓ Mobile Verified";

        document.getElementById('otp-input-group').style.display = 'none';
        
        const submitBtn = document.getElementById('signup-submit-btn');
        submitBtn.disabled = false;
        submitBtn.innerText = "Complete Registration";
    } else {
        alert("Invalid OTP code. Please enter the 6-digit code shown on screen.");
    }
}

// Submit Signup for All Roles
async function submitSignup() {
    if (!isMobileVerified) {
        alert("Please send and verify your mobile OTP before submitting.");
        return;
    }

    const phone = document.getElementById('su-phone').value.trim();
    const password = document.getElementById('su-pass').value.trim();
    const name = document.getElementById('su-name')?.value.trim() || 'User';

    if (!phone || !password) {
        alert("Mobile number and password are required.");
        return;
    }

    let endpoint = `${API_BASE_URL}/auth/register`;
    let payload = { phone: phone, password: password, role: currentRoleType };

    // Role-specific payload mapping
    if (currentRoleType === 'farmer') {
        payload.role = 'farmer';
    } else if (currentRoleType === 'fpo') {
        payload.role = 'fpo';
    } else if (currentRoleType === 'consumer' || currentRoleType === 'bulk_buyer') {
        endpoint = `${API_BASE_URL}/buyer/auth/signup`;
        payload = {
            phone: phone,
            password: password,
            buyer_type: currentRoleType === 'consumer' ? 'consumer' : 'bulk_buyer',
            full_name_or_contact: name,
            business_name: document.getElementById('su-biz-name')?.value || null,
            business_type: document.getElementById('su-biz-type')?.value || null,
            gstin: document.getElementById('su-gstin')?.value || null,
            monthly_quantity_approx: document.getElementById('su-qty')?.value || null
        };
    } else if (currentRoleType === 'driver') {
        endpoint = `${API_BASE_URL}/driver/auth/signup`;
        payload = {
            phone: phone,
            password: password,
            full_name: name,
            city: document.getElementById('su-city')?.value || 'Default City',
            district: 'District A',
            pincodes_served: '110001',
            vehicle_type: document.getElementById('su-vehicle-type')?.value || 'tempo',
            vehicle_number: document.getElementById('su-vehicle-no')?.value || ('REG-' + Math.floor(1000 + Math.random() * 9000)),
            load_capacity_kg: parseFloat(document.getElementById('su-capacity')?.value || 500)
        };
    }

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        logConsole(data);

        if (res.status === 200 || res.status === 201 || data.status === 'success') {
            alert(`Account registered successfully as ${currentRoleType.toUpperCase()}! Redirecting to login...`);
            showView('view-login');
            document.getElementById('login-phone').value = phone;
        } else {
            alert(data.message || "Registration failed. Please check inputs.");
        }
    } catch (err) {
        logConsole({ status: "error", message: "Failed to connect to backend server." });
    }
}

// Dynamic Login Routing
async function handleLogin() {
    const selectedRole = document.getElementById('login-role').value;
    const phone = document.getElementById('login-phone').value.trim();
    const password = document.getElementById('login-pass').value.trim();

    if (!phone || !password) {
        alert("Please enter both mobile number and password.");
        return;
    }

    let endpoint = `${API_BASE_URL}/auth/login`;
    if (selectedRole === 'buyer') endpoint = `${API_BASE_URL}/buyer/auth/login`;
    else if (selectedRole === 'driver') endpoint = `${API_BASE_URL}/driver/auth/login`;
    else if (selectedRole === 'admin') endpoint = `${API_BASE_URL}/admin/auth/login`;

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone, password: password })
        });
        const data = await res.json();
        logConsole(data);

        if (res.status === 200 || data.status === 'success') {
            currentUser = data.data || { phone: phone, role: selectedRole, approval_status: 'pending' };
            if (!currentUser.role) currentUser.role = selectedRole;

            document.getElementById('logout-btn').style.display = 'inline-block';
            loadDashboard(currentUser.role, currentUser.approval_status || 'pending');
        } else {
            alert(data.message || "Invalid mobile number or password.");
        }
    } catch (err) {
        logConsole({ status: "error", message: "Backend connection error." });
    }
}

function handleLogout() {
    currentUser = null;
    document.getElementById('logout-btn').style.display = 'none';
    showView('view-landing');
}

function loadDashboard(role, status) {
    showView('view-dashboard');
    const nav = document.getElementById('dash-nav-buttons');
    const content = document.getElementById('dash-main-content');

    nav.innerHTML = `
        <button onclick="fetchListings()">Marketplace Listings</button>
        <button onclick="fetchMandiPrices()">Mandi Rates</button>
    `;

    content.innerHTML = `
        <div class="card">
            <h3>Logged in as: ${role.toUpperCase()}</h3>
            <p>Account Status: <strong>${status}</strong></p>
            <p>Use the navigation options to test marketplace features.</p>
        </div>
    `;
}

async function fetchListings() {
    try {
        const res = await fetch(`${API_BASE_URL}/listings`);
        const data = await res.json();
        logConsole(data);
        document.getElementById('dash-main-content').innerHTML = `<div class="card"><h3>Active Crop Listings</h3><pre>${JSON.stringify(data.data, null, 2)}</pre></div>`;
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
