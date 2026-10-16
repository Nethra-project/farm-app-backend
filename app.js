const API_BASE_URL = 'http://127.0.0.1:5000';
let activeRole = '';
let isOtpVerified = false;
let currentLang = 'en';

function showView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
}

function toggleLanguage() {
    currentLang = currentLang === 'en' ? 'hi' : 'en';
    document.getElementById('ui-title').innerText = currentLang === 'en' ? '🌾 Krishi Bazaar Portal' : '🌾 कृषि बाजार पोर्टल';
    document.getElementById('hero-title').innerText = currentLang === 'en' ? 'Direct Agricultural Marketplace' : 'प्रत्यक्ष कृषि बाजार';
    document.getElementById('hero-desc').innerText = currentLang === 'en' ? 'Empowering Farmers, FPOs, Buyers, and Drivers with transparent trade and direct logistics.' : 'किसानों, एफपीओ, खरीदारों और ड्राइवरों को पारदर्शी व्यापार के साथ सशक्त बनाना।';
}

function initSignup(role) {
    activeRole = role;
    isOtpVerified = false;
    document.getElementById('signup-heading').innerText = `${role.toUpperCase()} Registration`;
    document.getElementById('btn-complete-reg').disabled = true;
    document.getElementById('otp-input-group').style.display = 'none';

    let html = `<input type="password" id="su-pass" placeholder="Create Password (Required)">`;

    if (role === 'farmer') {
        html += `
            <input type="text" id="su-name" placeholder="Full Name">
            <input type="text" id="su-village" placeholder="Village">
            <input type="text" id="su-district" placeholder="District">
            <input type="text" id="su-state" placeholder="State">
            <input type="text" id="su-pincode" placeholder="Pincode">
            <input type="text" id="su-crops" placeholder="Crops Grown (e.g., Wheat, Paddy)">
            <input type="text" id="su-payment" placeholder="UPI ID or Bank Account & IFSC">
            <input type="text" id="su-fpo" placeholder="FPO Name (Optional)">
        `;
    } else if (role === 'fpo') {
        html += `
            <input type="text" id="su-fpo-name" placeholder="FPO Name">
            <select id="su-reg-type"><option value="company">Company</option><option value="society">Society</option><option value="cooperative">Cooperative</option></select>
            <input type="text" id="su-reg-no" placeholder="Registration Number">
            <input type="number" id="su-reg-year" placeholder="Registration Year">
            <input type="text" id="su-contact" placeholder="Contact Person Name">
            <input type="text" id="su-desig" placeholder="Designation">
            <input type="text" id="su-address" placeholder="Office Address, District, State, Pincode">
            <input type="number" id="su-members" placeholder="Number of Member Farmers">
            <input type="text" id="su-crops-handled" placeholder="Crops Handled">
            <input type="text" id="su-bank" placeholder="Bank Account & IFSC">
        `;
    } else if (role === 'consumer' || role === 'bulk_buyer') {
        html += `
            <input type="text" id="su-fullname" placeholder="Full Name or Contact Person">
            ${role === 'bulk_buyer' ? '<input type="text" id="su-biz" placeholder="Business Name"><input type="text" id="su-gstin" placeholder="GSTIN (Optional)">' : ''}
            <input type="text" id="su-addr" placeholder="Delivery Address & Landmark">
            <input type="text" id="su-city" placeholder="City">
            <input type="text" id="su-pin" placeholder="Pincode">
        `;
    } else if (role === 'driver') {
        html += `
            <input type="text" id="su-dname" placeholder="Full Name">
            <input type="text" id="su-dcity" placeholder="City & District">
            <input type="text" id="su-pincodes" placeholder="Pincodes Served (comma separated)">
            <select id="su-vehicle"><option value="bike">Bike</option><option value="tempo">Tempo</option><option value="pickup_truck">Pickup Truck</option><option value="mini_truck">Mini Truck</option></select>
            <input type="text" id="su-vno" placeholder="Vehicle Number">
            <input type="number" id="su-capacity" placeholder="Load Capacity in kg">
            <input type="text" id="su-payout" placeholder="UPI ID for Payouts">
        `;
    }

    document.getElementById('signup-form-container').innerHTML = html;
    showView('view-signup');
}

async function sendServerOTP() {
    const phone = document.getElementById('su-phone').value.trim();
    if (!phone || phone.length < 10) {
        alert("Please enter a valid 10-digit mobile number.");
        return;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/auth/send-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone })
        });
        const data = await res.json();
        if (res.ok) {
            alert(data.message);
            document.getElementById('otp-input-group').style.display = 'block';
        } else {
            alert(data.message || "Failed to send OTP.");
        }
    } catch (err) {
        alert("Network error connecting to backend server.");
    }
}

async function verifyServerOTP() {
    const phone = document.getElementById('su-phone').value.trim();
    const otp_code = document.getElementById('su-otp-code').value.trim();

    try {
        const res = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, otp_code })
        });
        const data = await res.json();
        if (res.ok) {
            isOtpVerified = true;
            document.getElementById('btn-complete-reg').disabled = false;
            alert("Mobile number verified successfully!");
        } else {
            alert(data.message || "Invalid OTP code.");
        }
    } catch (err) {
        alert("Verification network error.");
    }
}

async function submitUserRegistration() {
    if (!isOtpVerified) {
        alert("Please verify your mobile number with OTP first.");
        return;
    }

    const phone = document.getElementById('su-phone').value.trim();
    const password = document.getElementById('su-pass').value.trim();
    let payload = { phone, password, role: activeRole };

    if (activeRole === 'farmer') {
        payload.full_name = document.getElementById('su-name').value;
        payload.village = document.getElementById('su-village').value;
        payload.district = document.getElementById('su-district').value;
        payload.state = document.getElementById('su-state').value;
        payload.pincode = document.getElementById('su-pincode').value;
        payload.crops_grown = document.getElementById('su-crops').value;
        payload.payment_details = document.getElementById('su-payment').value;
        payload.fpo_name = document.getElementById('su-fpo').value;
    } else if (activeRole === 'fpo') {
        payload.fpo_name = document.getElementById('su-fpo-name').value;
        payload.registration_type = document.getElementById('su-reg-type').value;
        payload.registration_number = document.getElementById('su-reg-no').value;
        payload.registration_year = parseInt(document.getElementById('su-reg-year').value || 2021);
        payload.contact_person_name = document.getElementById('su-contact').value;
        payload.designation = document.getElementById('su-desig').value;
        payload.office_address = document.getElementById('su-address').value;
        payload.district = "District A";
        payload.state = "State A";
        payload.pincode = "110001";
        payload.member_farmer_count = parseInt(document.getElementById('su-members').value || 10);
        payload.crops_handled = document.getElementById('su-crops-handled').value;
        payload.bank_account_details = document.getElementById('su-bank').value;
    } else if (activeRole === 'consumer' || activeRole === 'bulk_buyer') {
        payload.full_name_or_contact = document.getElementById('su-fullname').value;
        payload.delivery_address = document.getElementById('su-addr').value;
        payload.city = document.getElementById('su-city').value;
        payload.pincode = document.getElementById('su-pin').value;
        if (activeRole === 'bulk_buyer') {
            payload.business_name = document.getElementById('su-biz').value;
            payload.gstin = document.getElementById('su-gstin').value;
        }
    } else if (activeRole === 'driver') {
        payload.full_name = document.getElementById('su-dname').value;
        payload.city = document.getElementById('su-dcity').value;
        payload.district = "District A";
        payload.pincodes_served = document.getElementById('su-pincodes').value;
        payload.vehicle_type = document.getElementById('su-vehicle').value;
        payload.vehicle_number = document.getElementById('su-vno').value;
        payload.load_capacity_kg = parseFloat(document.getElementById('su-capacity').value || 500);
        payload.payout_details = document.getElementById('su-payout').value;
    }

    try {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            alert("Registration successful! Please log in.");
            showView('view-login');
            document.getElementById('login-phone').value = phone;
        } else {
            alert(data.message || "Registration failed.");
        }
    } catch (err) {
        alert("Registration network failure.");
    }
}

async function executeLogin() {
    const identifier = document.getElementById('login-phone').value.trim();
    const password = document.getElementById('login-password').value.trim();

    try {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: identifier, password })
        });
        const data = await res.json();
        if (res.ok && data.token) {
            localStorage.setItem('krishi_token', data.token);
            document.getElementById('logout-btn').style.display = 'inline-block';
            renderDashboard(data.user);
        } else {
            alert(data.message || "Invalid login credentials.");
        }
    } catch (err) {
        alert("Login network failure.");
    }
}

function logoutUser() {
    localStorage.removeItem('krishi_token');
    document.getElementById('logout-btn').style.display = 'none';
    showView('view-landing');
}

function renderDashboard(user) {
    showView('view-dashboard');
    const notice = document.getElementById('approval-notice');
    if (user.approval_status === 'pending') {
        notice.style.display = 'block';
    } else {
        notice.style.display = 'none';
    }

    let html = `
        <h2>Welcome, ${user.role.toUpperCase()} Dashboard</h2>
        <p>Account Status: <span class="badge ${user.approval_status}">${user.approval_status}</span></p>
    `;

    if (user.role === 'farmer' || user.role === 'fpo') {
        html += `
            <div class="dashboard-grid">
                <div class="stat-card"><h4>Active Listings</h4><p class="value">0</p></div>
                <div class="stat-card"><h4>New Orders</h4><p class="value">0</p></div>
                <div class="stat-card"><h4>Total Earnings</h4><p class="value">₹0</p></div>
            </div>
            <div class="card">
                <h3>Farmer / FPO Operations</h3>
                <p>Manage your crop produce, review incoming orders, and track payouts.</p>
                <button class="btn-main" style="width: 200px;" onclick="alert('Listing creation wizard is ready.')">➕ Add New Crop Listing</button>
            </div>
        `;
    } else if (user.role === 'consumer' || user.role === 'bulk_buyer') {
        html += `
            <div class="dashboard-grid">
                <div class="stat-card"><h4>Active Orders</h4><p class="value">0</p></div>
                <div class="stat-card"><h4>Saved Addresses</h4><p class="value">1</p></div>
            </div>
            <div class="card">
                <h3>Browse Marketplace & Place Orders</h3>
                <p>Search fresh produce directly from verified farmers and FPOs.</p>
                <button class="btn-main" style="width: 200px;" onclick="alert('Marketplace catalog browser active.')">🛒 Browse Listings</button>
            </div>
        `;
    } else if (user.role === 'driver') {
        html += `
            <div class="dashboard-grid">
                <div class="stat-card"><h4>Available Jobs</h4><p class="value">0</p></div>
                <div class="stat-card"><h4>Today's Earnings</h4><p class="value">₹0</p></div>
            </div>
            <div class="card">
                <h3>Delivery & Transport Hub</h3>
                <p>Accept nearby pickup jobs and manage drop-off verification codes.</p>
                <button class="btn-main" style="width: 200px;" onclick="alert('Driver job feed active.')">🚚 View Available Jobs</button>
            </div>
        `;
    }

    document.getElementById('dashboard-container').innerHTML = html;
}
