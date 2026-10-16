import sqlite3

def init_database():
    conn = sqlite3.connect('farm_db.sqlite')
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        approval_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. OTP Codes Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS otp_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        otp_code TEXT NOT NULL,
        expires_at DATETIME NOT NULL,
        is_verified BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 3. Farmer Profiles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS farmer_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        village TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        pincode TEXT NOT NULL,
        crops_grown TEXT NOT NULL,
        payment_details TEXT NOT NULL,
        fpo_name TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # 4. FPO Profiles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fpo_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        fpo_name TEXT NOT NULL,
        registration_type TEXT NOT NULL,
        registration_number TEXT UNIQUE NOT NULL,
        registration_year INTEGER NOT NULL,
        contact_person_name TEXT NOT NULL,
        designation TEXT NOT NULL,
        office_address TEXT NOT NULL,
        district TEXT NOT NULL,
        state TEXT NOT NULL,
        pincode TEXT NOT NULL,
        member_farmer_count INTEGER DEFAULT 0,
        crops_handled TEXT NOT NULL,
        bank_account_details TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # 5. Buyer Profiles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS buyer_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        buyer_type TEXT NOT NULL,
        full_name_or_contact TEXT NOT NULL,
        business_name TEXT,
        gstin TEXT,
        delivery_address TEXT NOT NULL,
        city TEXT NOT NULL,
        pincode TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # 6. Driver Profiles
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS driver_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        city TEXT NOT NULL,
        pincodes_served TEXT NOT NULL,
        vehicle_type TEXT NOT NULL,
        vehicle_number TEXT UNIQUE NOT NULL,
        load_capacity_kg REAL NOT NULL,
        payout_details TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()
    print("Database tables initialized successfully!")

if __name__ == '__main__':
    init_database()
