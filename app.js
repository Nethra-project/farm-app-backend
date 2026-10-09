// Toggle Buyer category options based on selected role
function toggleRoleFields() {
    const role = document.getElementById('reg-role').value;
    const buyerContainer = document.getElementById('buyer-type-container');
    
    if (role === 'buyer') {
        buyerContainer.style.display = 'block';
    } else {
        buyerContainer.style.display = 'none';
    }
}

// Toggle extra business fields for Bulk Buyers
function toggleBulkBuyerFields() {
    const buyerType = document.getElementById('reg-buyer-type').value;
    const bulkFields = document.getElementById('bulk-buyer-fields');
    
    if (buyerType === 'bulk_buyer') {
        bulkFields.style.display = 'block';
    } else {
        bulkFields.style.display = 'none';
    }
}

// Updated Registration handler to support Retail vs Bulk Buyer payloads
async function handleRegister() {
    const role = document.getElementById('reg-role').value;
    const phone = document.getElementById('reg-phone').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-pass').value;

    let endpoint = `${API_BASE_URL}/auth/register`;
    let payload = { phone, email, password, role };

    // Direct to dedicated buyer onboarding route if role is Buyer
    if (role === 'buyer') {
        const buyerType = document.getElementById('reg-buyer-type').value;
        endpoint = `${API_BASE_URL}/buyer/auth/signup`;
        
        payload = {
            phone,
            email,
            password,
            buyer_type: buyerType,
            full_name_or_contact: phone // Defaulting to phone if name is blank
        };

        if (buyerType === 'bulk_buyer') {
            payload.business_name = document.getElementById('reg-business-name').value;
            payload.business_type = document.getElementById('reg-business-type').value;
            payload.gstin = document.getElementById('reg-gstin').value;
            payload.monthly_quantity_approx = document.getElementById('reg-monthly-qty').value;
        }
    }

    try {
        const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        displayResponse(await res.json());
    } catch (err) {
        displayResponse({ status: 'error', message: 'Backend connection failed' });
    }
}
