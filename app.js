const API_BASE_URL = 'http://127.0.0.1:5000';
let activeRole = '';
let isVerified = false;
let lang = 'en';

function log(data) {
    document.getElementById('console').innerText = JSON.stringify(data, null, 2);
}

function showView(id) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

function toggleLang() {
    lang = lang === 'en' ? 'hi' : 'en';
    document.getElementById('ui-title').innerText = lang === 'en' ? '🌾 Krishi Bazaar' : '🌾 कृषि बाजार';
    document.getElementById('ui-hero').innerText = lang === 'en' ? 'Direct Agricultural Marketplace' : 'प्रत्यक्ष कृषि बाजार';
}

function setupSignup(role) {
    activeRole = role;
    isVerified = false;
    document.getElementById('signup-header').innerText = `${role.toUpperCase()} Registration`;
    document.getElementById('btn-register').disabled = true;
    document.getElementById('otp-section').style.display = 'none';

    let html = `<input type="password" id="su-pass" placeholder="Password">`;
    if (role === 'farmer') {
        html += `<input type="text" id="su-name" placeholder="Full Name"><input type="text" id="su-village" placeholder="Village"><input type="text" id="su-district" placeholder="District"><input type="text" id="su-state" placeholder="State"><input type="text" id="su-pincode" placeholder="Pincode"><input type="text" id="su-crops" placeholder="Crops Grown"><input type="text" id="su-payment" placeholder="UPI ID / Bank & IFSC"><input type="text" id="su-fpo" placeholder="FPO Name (Optional)">`;
    } else if (role === 'fpo') {
        html += `<input type="text" id="su-fponame" placeholder="FPO Name"><select id="su-regtype"><option value="company">Company</option><option value="society">Society</option><option value="cooperative">Cooperative</option></select><input type="text" id="su-regno" placeholder="Registration Number"><input type="number" id="su-regyear" placeholder="Registration Year"><input type="text" id="su-contact" placeholder="Contact Person"><input type="text" id="su-desig" placeholder="Designation"><input type="text" id="su-address" placeholder="Office Address"><input type="text" id="su-fpo-district" placeholder="District"><input type="text" id="su-fpo-state" placeholder="State"><input type="text" id="su-fpo-pincode" placeholder="Pincode"><input type="number" id="su-members" placeholder="Member Farmer Count"><input type="text" id="su-cropshandled" placeholder="Crops Handled"><input type="text" id="su-bank" placeholder="Bank Account & IFSC">`;
    } else if (role === 'consumer' || role === 'bulk_buyer') {
        html += `<input type="text" id="su-fullname" placeholder="Full Name / Contact Person">${role === 'bulk_buyer' ? '<input type="text" id="su-biz" placeholder="Business Name"><input type="text" id="su-gstin" placeholder="GSTIN">' : ''}<input type="text" id="su-addr" placeholder="Delivery Address"><input type="text" id="su-city" placeholder="City"><input type="text" id="su-pin" placeholder="Pincode">`;
    } else if (role === 'driver') {
        html += `<input type="text" id="su-drivername" placeholder="Full Name"><input type="text" id="su-dcity" placeholder="City"><input type="text" id="su-pincodesserved" placeholder="Pincodes Served"><select id="su-vehicle"><option value="bike">Bike</option><option value="tempo">Tempo</option><option value="pickup_truck">Pickup Truck</option></select><input type="text" id="su-vno" placeholder="Vehicle Number"><input type="number" id="su-capacity" placeholder="Load Capacity (kg)"><input type="text" id="su-payout" placeholder="UPI ID for Payouts">`;
    }

    document.getElementById('signup-form-fields').innerHTML = html;
    showView('view-signup');
}

async function requestOTP() {
    const phone = document.getElementById('su-phone').value.trim();
    if (!phone) { alert("Enter phone number"); return; }

    const res = await fetch(`${API_BASE_URL}/auth/send-otp`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone })
    });
    const data = await res.json();
    log(data);
    if (res.ok) {
        document.getElementById('otp-section').style.display = 'block';
        alert("OTP sent! Use code: 123456");
    }
}

async function verifyOTP() {
    const phone = document.getElementById('su-phone').value.trim();
    const otp_code = document.getElementById('su-otp').value.trim();

    const res = await fetch(`${API_BASE_URL}/auth/verify-otp`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, otp_code })
    });
    const data = await res.json();
    log(data);
    if (res.ok) {
        isVerified = true;
        document.getElementById('btn-register').disabled = false;
        alert("OTP Verified Successfully!");
    } else {
        alert("Verification failed.");
    }
}

async function submitRegistration() {
    if (!isVerified) { alert("Verify OTP first"); return; }
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
        payload.fpo_name = document.getElementById('su-fponame').value;
        payload.registration_type = document.getElementById('su-regtype').value;
        payload.registration_number = document.getElementById('su-regno').value;
        payload.registration_year = parseInt(document.getElementById('su-regyear').value || 2021);
        payload.contact_person_name = document.getElementById('su-contact').value;
        payload.designation = document.getElementById('su-desig').value;
        payload.office_address = document.getElementById('su-address').value;
        payload.district = document.getElementById('su-fpo-district').value;
        payload.state = document.getElementById('su-fpo-state').value;
        payload.pincode = document.getElementById('su-fpo-pincode').value;
        payload.member_farmer_count = parseInt(document.getElementById('su-members').value || 10);
        payload.crops_handled = document.getElementById('su-cropshandled').value;
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
        payload.full_name = document.getElementById('su-drivername').value;
        payload.city = document.getElementById('su-dcity').value;
        payload.pincodes_served = document.getElementById('su-pincodesserved').value;
        payload.vehicle_type = document.getElementById('su-vehicle').value;
        payload.vehicle_number = document.getElementById('su-vno').value;
        payload.load_capacity_kg = parseFloat(document.getElementById('su-capacity').value || 500);
        payload.payout_details = document.getElementById('su-payout').value;
    }

    const res = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    log(data);
    if (res.ok) {
        alert("Registration complete! Please log in.");
        showView('view-login');
        document.getElementById('login-phone').value = phone;
    }
}

async function login() {
    const phone = document.getElementById('login-phone').value.trim();
    const password = document.getElementById('login-password').value.trim();

    const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone, password })
    });
    const data = await res.json();
    log(data);

    if (res.ok && data.token) {
        localStorage.setItem('token', data.token);
        document.getElementById('logout-btn').style.display = 'inline-block';
        showView('view-dashboard');
        document.getElementById('dashboard-body').innerHTML = `
            <h2>Welcome, ${data.user.role.toUpperCase()}</h2>
            <p>Approval Status: <strong>${data.user.approval_status}</strong></p>
            <p>JWT Authentication active.</p>
        `;
    } else {
        alert(data.message || "Login failed");
    }
}

function logout() {
    localStorage.removeItem('token');
    document.getElementById('logout-btn').style.display = 'none';
    showView('view-landing');
}
