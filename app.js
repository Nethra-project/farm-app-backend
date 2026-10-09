// Fixed Signup Execution
async function submitSignup() {
    const phone = document.getElementById('su-phone').value.trim();
    const password = document.getElementById('su-pass').value.trim();
    const name = document.getElementById('su-name')?.value.trim() || 'User';

    if (!phone || !password) {
        alert("Please enter both phone number and password.");
        return;
    }

    let endpoint = `${API_BASE_URL}/auth/register`;
    let payload = { phone: phone, password: password, role: currentRoleType };

    if (currentRoleType === 'consumer' || currentRoleType === 'bulk_buyer') {
        endpoint = `${API_BASE_URL}/buyer/auth/signup`;
        payload = {
            phone: phone,
            password: password,
            buyer_type: currentRoleType === 'consumer' ? 'consumer' : 'bulk_buyer',
            full_name_or_contact: name
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
            vehicle_number: 'REG-' + Math.floor(1000 + Math.random() * 9000),
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

        if (data.status === 'success' || res.status === 201 || res.status === 200) {
            alert(`Mobile Verification Successful for ${phone}! Please log in now.`);
            // Pre-fill login phone for smooth sign-in
            showView('view-login');
            document.getElementById('login-phone').value = phone;
        } else {
            alert(data.message || "Registration failed. Check console for details.");
        }
    } catch (err) {
        logConsole({ status: "error", message: "Failed to connect to backend API." });
    }
}

// Fixed Dynamic Role Login Handler
async function handleLogin() {
    const selectedRole = document.getElementById('login-role').value;
    const phone = document.getElementById('login-phone').value.trim();
    const password = document.getElementById('login-pass').value.trim();

    if (!phone || !password) {
        alert("Please enter both phone number and password.");
        return;
    }

    // Route login request to the correct blueprint endpoint
    let endpoint = `${API_BASE_URL}/auth/login`;
    if (selectedRole === 'buyer') {
        endpoint = `${API_BASE_URL}/buyer/auth/login`;
    } else if (selectedRole === 'driver') {
        endpoint = `${API_BASE_URL}/driver/auth/login`;
    } else if (selectedRole === 'admin') {
        endpoint = `${API_BASE_URL}/admin/auth/login`;
    }

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone, password: password })
        });
        const data = await res.json();
        logConsole(data);

        if (data.status === 'success' || res.status === 200) {
            currentUser = data.data || { phone: phone, role: selectedRole, approval_status: 'pending' };
            // Ensure proper role mapping
            if (!currentUser.role) currentUser.role = selectedRole;
            
            document.getElementById('logout-btn').style.display = 'inline-block';
            loadDashboard(currentUser.role, currentUser.approval_status || 'pending');
        } else {
            alert(data.message || "Invalid credentials or user not found.");
        }
    } catch (err) {
        logConsole({ status: "error", message: "Backend communication error." });
    }
}
